-- TO RUN: pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-2/DOTGOV-EXTRACTION-1995-FY2013-MIME-TEXT-ARCS-PART-00999-000003.arc.gz -p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ -p O_DATA_DIR=7OctTest4 climate3.pig
--Climate Change Pig Script

SET default_parallel 100;

SET mapreduce.map.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/ia-porky-jar-with-dependencies.jar;

REGISTER 'climatechange.py' USING jython AS myfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();
DEFINE SURTURL org.archive.porky.SurtUrlKey();

Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader() AS (key:chararray, value:chararray);

Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];

Archive = FILTER Archive BY m#'errorMessage' is null;

ExtractedCounts = FOREACH Archive GENERATE m#'url' AS src:chararray,
           SURTURL(m#'url') AS surt:chararray,
           REPLACE(m#'digest','sha1:','') AS checksum:chararray,
           m#'date' as date:chararray,
           m#'code'          AS code:chararray,
           m#'title'         AS title:chararray,
           m#'description'   AS description:chararray,
           m#'content'       AS content:chararray;

Meta = FILTER ExtractedCounts BY content MATCHES '.*natural\\sdisaster.*' OR content MATCHES '.*desertification.*' OR content MATCHES '.*climate\\schange.*' OR content MATCHES '.*pollution.*' OR content MATCHES '.*ocean\\sacidification.*' OR content MATCHES '.*anthropocene.*' OR content MATCHES '.*anthropogenic.*' OR content MATCHES '.*greenhouse\\sgas.*' OR content MATCHES '.*climategate.*' OR content MATCHES '.*climatic\\sresearch\\sunit.*' OR content MATCHES '.*CRU.*' OR content MATCHES '.*IPCC.*' OR content MATCHES '.*security\\sof\\sfood.*' OR content MATCHES '.*global\\swarming.*' OR content MATCHES '.*fresh\\swater.*' OR content MATCHES '.*forest\\sconservation.*' OR content MATCHES '.*food\\ssecurity.*';

Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

CountsJoinChecksum = JOIN Meta BY (surt, checksum), Checksum BY (surt, checksum);

FullCounts = FOREACH CountsJoinChecksum GENERATE
                        Checksum::surt as surt,
                        Meta::src as src,
                        Checksum::date as date,
                        Meta::title as title,
                        Meta::code as code,
                        Meta::description as description,
                        Meta::content as content;

STORE FullCounts INTO '$O_DATA_DIR';
