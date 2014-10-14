--Climate Change Pig Script

SET default_parallel 100;

SET mapreduce.map.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/ia-porky-jar-with-dependencies.jar;

--REGISTER '16JulyCoding.py' USING jython AS myfuncs;
--REGISTER '24July_V2.py' USING jython AS myfuncs;
--REGISTER '7August_test.py' USING jython AS myfuncs;
REGISTER '13Aug_stats_script.py' USING jython AS myfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE SURTURL org.archive.porky.SurtUrlKey();

Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader() AS (key:chararray, value:chararray);

Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];

Archive = FILTER Archive BY m#'errorMessage' is null;

ExtractedCounts = FOREACH Archive GENERATE myfuncs.Threat_countWords(m#'boiled'),
           m#'url' AS src:chararray,
           SURTURL(m#'url') AS surt:chararray,
           REPLACE(m#'digest','sha1:','') AS checksum:chararray,
           m#'date' as date:chararray,
           m#'content'       AS content:chararray;

Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

CountsJoinChecksum = JOIN ExtractedCounts BY (surt, checksum), Checksum BY (surt, checksum);

FullCounts = FOREACH CountsJoinChecksum GENERATE
                        ExtractedCounts::src as src,
                        Checksum::date as date,
                        ExtractedCounts::counts as counts,
                        ExtractedCounts::content as content;

GroupedCounts = GROUP FullCounts BY src;

GroupedCounts = FOREACH GroupedCounts GENERATE
      group AS src,
      FLATTEN(myfuncs.fillInCounts(FullCounts)) AS (year:int,
month:int, word:chararray, count:int, filled:int, afterlast:int, URLs:chararray);
--(datatype:chararray):
--(year:int, month:int, word:chararray, count:int, filled:int, afterlast:int, UR
Ls:chararray);

GroupedCounts2 = FOREACH GroupedCounts GENERATE
      year AS year, month AS month, word AS word, count AS cou
nt, afterlast AS afterlast, URLs AS URLs;

--STORE FullCounts INTO '$O_DATA_DIR';
STORE GroupedCounts2 INTO '$O_DATA_DIR';
--STORE CountsJoinChecksum INTO '$O_DATA_DIR';
