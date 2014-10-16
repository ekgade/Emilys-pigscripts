%default I_PARSED_DATA_DIR '/search/nara/congress112th/parsed/';
%default O_METATEXT_DATA_DIR '/search/nara/congress112th/analysis/metatext-from-parsed-captures.gz/';
%default I_WORDS_FILE 'pig/text/words.txt';

SET mapred.max.map.failures.percent 10;
SET mapred.reduce.slowstart.completed.maps 0.9

--CDH4
--REGISTER lib/webarchive-commons-jar-with-dependencies.jar;

--CDH3
--REGISTER lib/ia-web-commons-jar-with-dependencies-CDH3.jar;

REGISTER lib/ia-porky-jar-with-dependencies.jar;
REGISTER lib/tutorial.jar;
REGISTER lib/tokenize.py using jython as TOKENIZE;
DEFINE TOLOWER org.apache.pig.tutorial.ToLower();
DEFINE SURTURL org.archive.porky.SurtUrlKey();
DEFINE COMPRESSWHITESPACES org.archive.porky.CompressWhiteSpacesUDF();
DEFINE FROMJSON org.archive.porky.FromJSON();
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();

-- Load the metadata from the parsed data, which is JSON strings stored in a Hadoop SequenceFile.
Meta = LOAD '$I_PARSED_DATA_DIR' USING SequenceFileLoader() AS (key:chararray, value:chararray);

-- Convert the JSON strings into Pig Map objects.
Meta = FOREACH Meta GENERATE FROMJSON(value) AS m:[];

-- Only retain records where the errorMessage is not present.  Records
-- that failed to parse will be present in the input, but will have an
-- errorMessage property, so if it exists, skip the record.
Meta = FILTER Meta BY m#'errorMessage' is null;

-- Only retain the fields of interest.
Meta = FOREACH Meta GENERATE m#'url'           AS src:chararray,
			     m#'date'          AS timestamp:chararray,
			     m#'code'          AS code:chararray,
			     m#'title'         AS title:chararray,
			     m#'description'   AS description:chararray,
			     m#'content'      AS content:chararray;

-- get meta text only from HTTP 200 response pages
Meta = FILTER Meta BY code == '200';

-- canonicalize the URL
Meta = FOREACH Meta GENERATE SURTURL(src) as src,
			     ToDate(timestamp,'yyyyMMddHHmmss') as timestamp,
			     (title is null?'':title) as title,
			     (description is null?'':description) as description,
           (content is null?'':content) as content;

-- Put title, content and description into one field called Metatext

Meta = FOREACH Meta GENERATE src,
			     timestamp,
			     BagToString(TOBAG(title,description,content), ' ') as metatext;

Meta = FILTER Meta BY metatext is not null;

Meta = FOREACH Meta GENERATE src,
			     timestamp,
			     COMPRESSWHITESPACES(metatext) as metatext;

Meta = FILTER Meta BY metatext != '' AND metatext != ' ';

Docs = FOREACH Meta GENERATE src as src, timestamp as timestamp, FLATTEN(TOKENIZE(metatext)) as term;

DocWordTotals = FOREACH (GROUP Docs by (src)) GENERATE group as src, date as date, COUNT(term) as docTotal;

Store DocWordTotals into '$O_METATEXT_DATA_DIR';
