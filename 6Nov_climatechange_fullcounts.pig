SET default_parallel 100;

SET mapreduce.map.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/ia-porky-jar-with-dependencies.jar;

--REGISTER '16JulyCoding.py' USING jython AS myfuncs;
REGISTER 'climate_6nov.py' USING jython AS myfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE SURTURL org.archive.porky.SurtUrlKey();

Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader() AS (key:chararray, value:chararray);

Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];

Archive = FILTER Archive BY m#'errorMessage' is null;

ExtractedCounts = FOREACH Archive GENERATE myfuncs.pickURLs(m#'url'),
			                       m#'url' AS src:chararray,
			                       SURTURL(m#'url') as surt:chararray,
                             REPLACE(m#'digest','sha1:','') AS checksum:chararray,
                             m#'date' as date:chararray,
                             myfuncs.Threat_countWords(m#'boiled');

Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

CountsJoinChecksum = JOIN ExtractedCounts BY (surt, checksum), Checksum BY (surt, checksum);

FullCounts = FOREACH CountsJoinChecksum GENERATE
                        ExtractedCounts::src as src,
                        Checksum::date as date,
                        ExtractedCounts::counts as counts,
			ExtractedCounts::URLs as URLs;

GroupedCounts = GROUP FullCounts BY src;

STORE GroupedCounts INTO '$O_DATA_DIR';
