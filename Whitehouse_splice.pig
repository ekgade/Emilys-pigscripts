SET default_parallel 100;

SET mapreduce.map.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/ia-porky-jar-with-dependencies.jar;

REGISTER 'Whitehouse_splice.py' USING jython AS myfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE SURTURL org.archive.porky.SurtUrlKey();

-- load parsed data file, either bucket or single WARC file
Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader() AS (key:chararray, value:chararray);

Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];

-- Only retain records where the errorMessage is not present.  Records
-- that failed to parse will be present in the input, but will have an
-- errorMessage property, so if it exists, skip the record.
Meta = FILTER Archive BY m#'errorMessage' is null;

-- Only retain the fields of interest.
Meta = FOREACH Meta GENERATE m#'url' AS src:chararray,
			     REPLACE(m#'digest','sha1:','') AS checksum:chararray,
					 m#'date'          AS date:chararray,
					 SURTURL(m#'url')  AS surt:chararray,
			     m#'code'          AS code:chararray,
			     m#'title'         AS title:chararray,
			     m#'description'   AS description:chararray,
			     m#'content'       AS content:chararray;

-- Set up to join with Checkedsum Data; make sure names of fields are the same
Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

CountsJoinChecksum = JOIN Meta BY (surt, checksum), Checksum BY (surt, checksum);

-- canonicalize the URL
Meta = FOREACH CountsJoinChecksum GENERATE SURTURL(src) as src,
			     ToDate(timestamp,'yyyyMMddHHmmss') as timestamp,
			     (title is null?'':title) as title,
			     (description is null?'':description) as description,
			     (content is null?'':content) as content;

GroupedCounts = GROUP Meta BY src;

STORE GroupedCounts INTO '$O_DATA_DIR';
