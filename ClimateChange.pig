--Climate Change Pig Script

SET default_parallel 100;

SET mapreduce.map.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/ia-porky-jar-with-dependencies.jar;

--REGISTER '16JulyCoding.py' USING jython AS myfuncs;
--REGISTER '24July_V2.py' USING jython AS myfuncs;
--REGISTER '7August_test.py' USING jython AS myfuncs;
REGISTER 'climatechange.py' USING jython AS myfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE SURTURL org.archive.porky.SurtUrlKey();

Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader() AS (key:chararray, value:chararray);

Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];

Archive = FILTER Archive BY m#'errorMessage' is null;

--ExtractedCounts = FOREACH Archive

Test = FOREACH Archive GENERATE wordmatch AS myfuncs.ClimateChangeWords(m#'boiled');
Joined = JOIN Test BY (wordmatch), ExtractedCounts BY (wordmatch);

ExtractedCounts = FOREACH Archive GENERATE wordmatch AS myfuncs.ClimateChangeWords(m#'boiled');
           m#'url' AS src:chararray,
           SURTURL(m#'url') AS surt:chararray,
           REPLACE(m#'digest','sha1:','') AS checksum:chararray,
           m#'date' as date:chararray,
           m#'code'          AS code:chararray,
           m#'title'         AS title:chararray,
           m#'description'   AS description:chararray,
           m#'content'       AS content:chararray;

Test = FOREACH Archive GENERATE wordmatch AS myfuncs.ClimateChangeWords(m#'boiled');
Joined = JOIN Test BY (wordmatch, content), ExtractedCounts BY (wordmatch, content)

Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

CountsJoinChecksum = JOIN ExtractedCounts BY (surt, checksum), Checksum BY (surt, checksum);


FullCounts = FOREACH CountsJoinChecksum GENERATE
                        Checksum::surt as surt,
                        ExtractedCounts::src as src,
                        Checksum::date as date,
                        ExtractedCounts::counts as counts,
                        ExtractedCounts::title as title,
                        ExtractedCounts::code as code,
                        ExtractedCounts::description as description,
                        ExtractedCounts::content as content;

STORE FullCounts INTO '$O_DATA_DIR';
