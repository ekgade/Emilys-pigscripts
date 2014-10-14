-- To Run: use pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-0/ -
p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ -p O_DATA_DIR=output0_13Aug file
_to_counts_plus_URLs.pig


SET default_parallel 100;

SET mapreduce.map.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/ia-porky-jar-with-dependencies.jar;

REGISTER 'Whitehouse_splice.py' USING jython AS myfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE SURTURL org.archive.porky.SurtUrlKey();

-- load parsed data file, either bucket or single WARC file
Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader() AS (key:chararray, va
lue:chararray);

Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];

-- Only retain records where the errorMessage is not present.  Records
-- that failed to parse will be present in the input, but will have an
-- errorMessage property, so if it exists, skip the record.
Meta = FILTER Archive BY m#'errorMessage' is null;

-- Only retain the fields of interest
Meta = FOREACH Meta GENERATE myfuncs.pickURLs(m#'url'),
			     m#'url' 	       AS src:chararray,
			     REPLACE(m#'digest','sha1:','') AS checksum:chararray,
		 	     m#'date' 	       AS date:chararray,
			     SURTURL(m#'url')  AS surt:chararray,
			     m#'code'          AS code:chararray,
			     m#'title'         AS title:chararray,
			     m#'description'   AS description:chararray,
			     m#'content'       AS content:chararray;

-- Set up to join with Checkedsum Data; make sure names of fields are the same
Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

CountsJoinChecksum = JOIN Meta BY (surt, checksum), Checksum BY (surt, checksum);

FullCounts = FOREACH CountsJoinChecksum GENERATE
			Checksum::surt as surt,
                        Meta::src as src,
												Meta::title as title,
                        Checksum::date as date,
                        Meta::content as content;

-- GroupedCounts = GROUP FullCounts BY src;

-- GroupedCounts = FOREACH GroupedCounts GENERATE
--			group AS src,
--			FLATTEN(FullCounts) AS (surt:chararray, date:int, title:chararray, content:chararray);

STORE FullCounts INTO '$O_DATA_DIR';
