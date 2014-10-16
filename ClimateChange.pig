-- Climate Change Pig Script: Flags all captures whose content includes at least one mention of the term climate change and stores the output
-- For questions contact ekgade@uw.edu

-- TO RUN = type this into the command line: pig -p I_PARSED_DATA=/dataset-derived/gov/parsed/arcs/bucket-2/DOTGOV-EXTRACTION-1995-FY2013-MIME-TEXT-ARCS-PART-00999-000003.arc.gz -p I_CHECKSUM_DATA=/dataset/gov/url-ts-checksum/ -p O_DATA_DIR=7OctTest4 climate3.pig
-- make sure that your file paths are in the right place and that you start in the right directory (it doesnt give you clear errors about this)

-- These first four lines are defaults and also help with memory (if you dont have them, sometimes the cluster kicks you out)
SET default_parallel 100;

SET mapreduce.map.memory.mb 8192;
SET mapred.max.map.failures.percent 10;
REGISTER lib/ia-porky-jar-with-dependencies.jar;

-- This is how you would call out a to a python script with a designated function if you wanted to
-- I used this for RegEx matching but its much slower so I switched to the long "or" statement you see below
-- REGISTER 'climatechange.py' USING jython AS myfuncs;

DEFINE FROMJSON org.archive.porky.FromJSON();

-- The sequence file loader pulls the files out of the ARC/WARC format and makes them readable
DEFINE SequenceFileLoader org.archive.porky.SequenceFileLoader();

-- This flips the URL back to front so the important parts are at the beginning e.g. gov.whitehouse.frontpage......
DEFINE SURTURL org.archive.porky.SurtUrlKey();

-- when you load data, you have to use the same "name" for the data that you do in the command line command
Archive = LOAD '$I_PARSED_DATA' USING SequenceFileLoader() AS (key:chararray, value:chararray);

-- generating the m# fields helps process the crazy .gz format into fields you can recognize (e.g. title; content)
Archive = FOREACH Archive GENERATE FROMJSON(value) AS m:[];

-- this drops any files that return an error message
Archive = FILTER Archive BY m#'errorMessage' is null;

-- this is saying for each value and key pair, pull out the following fields.
ExtractedCounts = FOREACH Archive GENERATE m#'url' AS src:chararray,
           SURTURL(m#'url') AS surt:chararray,
           REPLACE(m#'digest','sha1:','') AS checksum:chararray,
           m#'date'          AS date:chararray,
           m#'code'          AS code:chararray,
           m#'title'         AS title:chararray,
           m#'description'   AS description:chararray,
           m#'content'       AS content:chararray;

-- This takes each of the previous tuples (the url, date, content, etc.) and searches
-- through the content field looking for any RegEx matches to these terms
-- If it finds one, it keeps it; otherwise "filter" drops the file
Meta = FILTER ExtractedCounts BY content MATCHES '.*natural\\sdisaster.*' OR content MATCHES '.*desertification.*' OR content MATCHES '.*climate\\schange.*' OR content MATCHES '.*pollution.*' OR content MATCHES '.*ocean\\sacidification.*' OR content MATCHES '.*anthropocene.*' OR content MATCHES '.*anthropogenic.*' OR content MATCHES '.*greenhouse\\sgas.*' OR content MATCHES '.*climategate.*' OR content MATCHES '.*climatic\\sresearch\\sunit.*' OR content MATCHES '.*CRU.*' OR content MATCHES '.*IPCC.*' OR content MATCHES '.*security\\sof\\sfood.*' OR content MATCHES '.*global\\swarming.*' OR content MATCHES '.*fresh\\swater.*' OR content MATCHES '.*forest\\sconservation.*' OR content MATCHES '.*food\\ssecurity.*';

-- This loads in the checkSum data. Again, make sure the $Icheckedsum matches the name you gave it in the command line
-- (it can be any name so long as they match)
Checksum = LOAD '$I_CHECKSUM_DATA' USING PigStorage() AS (surt:chararray, date:chararray, checksum:chararray);

-- This joins the CheckedSum cites with the other cites
CountsJoinChecksum = JOIN Meta BY (surt, checksum), Checksum BY (surt, checksum);

-- This reconstructs the fields for each checksum joined file - effectively creating duplicates for every time there was a capture
FullCounts = FOREACH CountsJoinChecksum GENERATE
                        Checksum::surt as surt,
                        Meta::src as src,
                        Checksum::date as date,
                        Meta::title as title,
                        Meta::code as code,
                        Meta::description as description,
                        Meta::content as content;

-- This stores the counts the file name you gave it
-- The "using pigstorage" function allows you to set your own delimiters.
-- I chose one with Unicode because I was worried commas/tabs would show up in the ext
STORE FullCounts INTO '$O_DATA_DIR' USING PigStorage('\u0001');
