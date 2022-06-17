--  ResearchAssistantCandidate :- boxminus_[0,5]UndergraduateStudent(x)

CREATE TEMP TABLE undergraduatestudent_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS personname, left_val AS endpoint FROM undergraduatestudent) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS personname, right_val AS endpoint FROM undergraduatestudent);

CREATE TEMP TABLE undergraduatestudent_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM undergraduatestudent_edges;

CREATE TEMP TABLE undergraduatestudent_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM undergraduatestudent_edges_stepone 
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE undergraduatestudent_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM undergraduatestudent_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE researchassistantcandidate_view_one AS 
    SELECT personname, (ledge+5) AS ledge, lendpointtype, redge, rendpointtype FROM undergraduatestudent_edges_star WHERE ledge+5 < redge OR (ledge+5 = redge AND lendpointtype = 1 AND rendpointtype = 4);
	
	

--  ResearchAssistantCandidate :- diamondminus_[0,2]graduatestudent(x)

CREATE TEMP TABLE graduatestudent_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS personname, left_val AS endpoint FROM graduatestudent) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS personname, right_val AS endpoint FROM graduatestudent);

CREATE TEMP TABLE graduatestudent_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM graduatestudent_edges;

CREATE TEMP TABLE graduatestudent_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM graduatestudent_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE graduatestudent_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM graduatestudent_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;
	
CREATE TEMP TABLE researchassistantcandidate_view_two AS 
    SELECT personname, ledge, lendpointtype, (redge+2) AS redge, rendpointtype FROM graduatestudent_edges_star;
	
	
	
--  ResearchAssistantCandidate :- boxplus_[0,2]teachingassistant(x)

CREATE TEMP TABLE teachingassistant_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS personname, left_val AS endpoint FROM teachingassistant) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS personname, right_val AS endpoint FROM teachingassistant);

CREATE TEMP TABLE teachingassistant_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM teachingassistant_edges;

CREATE TEMP TABLE teachingassistant_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM teachingassistant_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE teachingassistant_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM teachingassistant_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE researchassistantcandidate_view_three AS 
    SELECT personname, ledge, lendpointtype, (redge-2) AS redge, rendpointtype FROM teachingassistant_edges_star WHERE ledge < redge - 2 OR (ledge = redge - 2 AND lendpointtype = 1 AND rendpointtype = 4);
	
	
--  Coalesce ResearchAssistantCandidate

CREATE TEMP TABLE researchassistantcandidate_view_u AS 
    (SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM researchassistantcandidate_view_one) 
    UNION 
	(SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM researchassistantcandidate_view_two) 
	UNION 
	(SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM researchassistantcandidate_view_three);
	
	
CREATE TEMP TABLE researchassistantcandidate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, personname, ledge AS endpoint FROM researchassistantcandidate_view_u) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, personname, redge AS endpoint FROM researchassistantcandidate_view_u);

CREATE TEMP TABLE researchassistantcandidate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM researchassistantcandidate_edges;

CREATE TEMP TABLE researchassistantcandidate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM researchassistantcandidate_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE researchassistantcandidate_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM researchassistantcandidate_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;
	
	

--  ResearchAssistant(x) :- boxminus_[0,5]researchassistantcandidate(x)

CREATE TEMP TABLE researchassistant_view_one AS 
    SELECT personname, (ledge+5) AS ledge, lendpointtype, redge, rendpointtype FROM researchassistantcandidate_edges_star WHERE ledge+5 < redge OR (ledge+5 = redge AND lendpointtype = 1 AND rendpointtype = 4);


--  ResearchAssistant(x) :- publicationauthor(y,x), boxminus_[0,1]researchassistantcandidate(x)

CREATE TEMP TABLE publicationauthor_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS pubname, entity[2] AS personname, left_val AS endpoint FROM publicationauthor) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS pubname, entity[2] AS personname, right_val AS endpoint FROM publicationauthor);

CREATE TEMP TABLE publicationauthor_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY pubname, personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY pubname, personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY pubname, personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY pubname, personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, pubname, personname FROM publicationauthor_edges;

CREATE TEMP TABLE publicationauthor_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, pubname, personname FROM publicationauthor_edges_stepone 
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE publicationauthor_edges_star AS 
    SELECT pubname, personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT pubname, personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY pubname, personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY pubname, personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM publicationauthor_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE boxminus_zero_one_researchassistantcandidate_edges_star AS 
    SELECT personname, (ledge+1) AS ledge, lendpointtype, redge, rendpointtype FROM researchassistantcandidate_edges_star WHERE ledge+1 < redge OR (ledge+1 = redge AND lendpointtype = 1 AND rendpointtype = 4);


CREATE TEMP TABLE researchassistant_view_two_pre AS 
    SELECT publicationauthor_edges_star.personname, 
	       greatest(publicationauthor_edges_star.ledge, boxminus_zero_one_researchassistantcandidate_edges_star.ledge) AS ledge, 
	       least(publicationauthor_edges_star.redge, boxminus_zero_one_researchassistantcandidate_edges_star.redge) AS redge, 
		   CASE 
		       WHEN publicationauthor_edges_star.ledge = greatest(publicationauthor_edges_star.ledge, boxminus_zero_one_researchassistantcandidate_edges_star.ledge) AND publicationauthor_edges_star.lendpointtype = 3 THEN 3 
			   WHEN boxminus_zero_one_researchassistantcandidate_edges_star.ledge = greatest(publicationauthor_edges_star.ledge, boxminus_zero_one_researchassistantcandidate_edges_star.ledge) AND boxminus_zero_one_researchassistantcandidate_edges_star.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN publicationauthor_edges_star.redge = least(publicationauthor_edges_star.redge, boxminus_zero_one_researchassistantcandidate_edges_star.redge) AND publicationauthor_edges_star.rendpointtype = 2 THEN 2
		       WHEN boxminus_zero_one_researchassistantcandidate_edges_star.redge = least(publicationauthor_edges_star.redge, boxminus_zero_one_researchassistantcandidate_edges_star.redge) AND boxminus_zero_one_researchassistantcandidate_edges_star.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM publicationauthor_edges_star, boxminus_zero_one_researchassistantcandidate_edges_star 
    WHERE greatest(publicationauthor_edges_star.ledge, boxminus_zero_one_researchassistantcandidate_edges_star.ledge) <= least(publicationauthor_edges_star.redge, boxminus_zero_one_researchassistantcandidate_edges_star.redge) 
	      AND 
		  publicationauthor_edges_star.personname = boxminus_zero_one_researchassistantcandidate_edges_star.personname;

CREATE TEMP TABLE researchassistant_view_two AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM researchassistant_view_two_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


--  Coalesce ResearchAssistant

CREATE TEMP TABLE researchassistant_view_u AS 
    (SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM researchassistant_view_one) 
    UNION 
	(SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM researchassistant_view_two);
	
	
CREATE TEMP TABLE researchassistant_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, personname, ledge AS endpoint FROM researchassistant_view_u) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, personname, redge AS endpoint FROM researchassistant_view_u) 
    UNION ALL 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS personname, left_val AS endpoint FROM researchassistant) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS personname, right_val AS endpoint FROM researchassistant);


CREATE TEMP TABLE researchassistant_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM researchassistant_edges;

CREATE TEMP TABLE researchassistant_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM researchassistant_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE researchassistant_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM researchassistant_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;
















--  LecturerCandidate(x) :- boxminus_[0,2]ResearchAssistant(x) 

CREATE TEMP TABLE lecturercandidate_view_one AS 
    SELECT personname, (ledge+2) AS ledge, lendpointtype, redge, rendpointtype FROM researchassistant_edges_star WHERE ledge+2 < redge OR (ledge+2 = redge AND lendpointtype = 1 AND rendpointtype = 4);

--  LecturerCandidate(x) :- boxminus_[0,4]ResearchAssistantCandidate(x)

CREATE TEMP TABLE lecturercandidate_view_two AS 
    SELECT personname, (ledge+4) AS ledge, lendpointtype, redge, rendpointtype FROM researchassistantcandidate_edges_star WHERE ledge+4 < redge OR (ledge+4 = redge AND lendpointtype = 1 AND rendpointtype = 4);


--  LecturerCandidate(x) :- boxminus_[0,1]GraduateStudent(x), PublicationAuthor(y,x) Since_(0,1] Publication(y)

CREATE TEMP TABLE boxminus_zero_one_graduatestudent_edges_star AS 
    SELECT personname, (ledge+1) AS ledge, lendpointtype, redge, rendpointtype FROM graduatestudent_edges_star WHERE ledge+1 < redge OR (ledge+1 = redge AND lendpointtype = 1 AND rendpointtype = 4);


CREATE TEMP TABLE publication_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS pubname, left_val AS endpoint FROM publication) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS pubname, right_val AS endpoint FROM publication);


CREATE TEMP TABLE publication_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY pubname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY pubname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY pubname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY pubname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, pubname FROM publication_edges;

CREATE TEMP TABLE publication_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, pubname FROM publication_edges_stepone 
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE publication_edges_star AS 
    SELECT pubname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT pubname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY pubname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY pubname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM publication_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;
	
	
	
	
	
	
	
CREATE TEMP TABLE publicationauthor_intersects_publication AS
    SELECT personname, ledge, lendpointtype, redge, rendpointtype, publicationauthorledge, publicationauthorredge  
	FROM (
		SELECT publicationauthor_edges_star.personname,
	       greatest(publicationauthor_edges_star.ledge, publication_edges_star.ledge) AS ledge,
	       least(publicationauthor_edges_star.redge, publication_edges_star.redge) AS redge,
		   CASE
			   WHEN publication_edges_star.ledge = greatest(publicationauthor_edges_star.ledge, publication_edges_star.ledge) AND publication_edges_star.lendpointtype = 3 THEN 3
			   ELSE 1
		   END AS lendpointtype,
		   CASE
		       WHEN publication_edges_star.redge = least(publicationauthor_edges_star.redge, publication_edges_star.redge) AND publication_edges_star.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype, 
		   publicationauthor_edges_star.ledge AS publicationauthorledge, 
		   publicationauthor_edges_star.redge AS publicationauthorredge 
        FROM publicationauthor_edges_star, publication_edges_star
        WHERE greatest(publicationauthor_edges_star.ledge, publication_edges_star.ledge) <= least(publicationauthor_edges_star.redge, publication_edges_star.redge)
	          AND
		      publicationauthor_edges_star.pubname = publication_edges_star.pubname) AS innerTable 
	WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);
	
	
	
	
	


CREATE TEMP TABLE publicationauthor_since_zero_one_publication_pre AS 
    SELECT personname, 
	    greatest(publicationauthor_intersects_publication.ledge, publicationauthor_intersects_publication.publicationauthorledge) AS ledge, 
		least(publicationauthor_intersects_publication.redge + 1, publicationauthor_intersects_publication.publicationauthorredge) AS redge, 
		CASE 
		    WHEN publicationauthor_intersects_publication.ledge >= publicationauthor_intersects_publication.publicationauthorledge THEN 3 
			ELSE 1
		END AS lendpointtype, 
		CASE 
		    WHEN publicationauthor_intersects_publication.rendpointtype = 2 AND publicationauthor_intersects_publication.redge + 1 <= publicationauthor_intersects_publication.publicationauthorredge THEN 2 
			ELSE 4
		END AS rendpointtype 
	FROM publicationauthor_intersects_publication  
	WHERE greatest(publicationauthor_intersects_publication.ledge, publicationauthor_intersects_publication.publicationauthorledge) <= least(publicationauthor_intersects_publication.redge + 1, publicationauthor_intersects_publication.publicationauthorredge);
	
CREATE TEMP TABLE publicationauthor_since_zero_one_publication AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM publicationauthor_since_zero_one_publication_pre 
	WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


CREATE TEMP TABLE lecturercandidate_view_three_pre AS 
    SELECT boxminus_zero_one_graduatestudent_edges_star.personname, 
	       greatest(boxminus_zero_one_graduatestudent_edges_star.ledge, publicationauthor_since_zero_one_publication.ledge) AS ledge, 
	       least(boxminus_zero_one_graduatestudent_edges_star.redge, publicationauthor_since_zero_one_publication.redge) AS redge, 
		   CASE 
		       WHEN boxminus_zero_one_graduatestudent_edges_star.ledge = greatest(boxminus_zero_one_graduatestudent_edges_star.ledge, publicationauthor_since_zero_one_publication.ledge) AND boxminus_zero_one_graduatestudent_edges_star.lendpointtype = 3 THEN 3 
			   WHEN publicationauthor_since_zero_one_publication.ledge = greatest(boxminus_zero_one_graduatestudent_edges_star.ledge, publicationauthor_since_zero_one_publication.ledge) AND publicationauthor_since_zero_one_publication.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN boxminus_zero_one_graduatestudent_edges_star.redge = least(boxminus_zero_one_graduatestudent_edges_star.redge, publicationauthor_since_zero_one_publication.redge) AND boxminus_zero_one_graduatestudent_edges_star.rendpointtype = 2 THEN 2
		       WHEN publicationauthor_since_zero_one_publication.redge = least(boxminus_zero_one_graduatestudent_edges_star.redge, publicationauthor_since_zero_one_publication.redge) AND publicationauthor_since_zero_one_publication.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM boxminus_zero_one_graduatestudent_edges_star, publicationauthor_since_zero_one_publication  
    WHERE greatest(boxminus_zero_one_graduatestudent_edges_star.ledge, publicationauthor_since_zero_one_publication.ledge) <= least(boxminus_zero_one_graduatestudent_edges_star.redge, publicationauthor_since_zero_one_publication.redge) 
	      AND 
		  boxminus_zero_one_graduatestudent_edges_star.personname = publicationauthor_since_zero_one_publication.personname;

CREATE TEMP TABLE lecturercandidate_view_three AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM lecturercandidate_view_three_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


--  Coalesce lecturercandidate

CREATE TEMP TABLE lecturercandidate_view_u AS 
    (SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM lecturercandidate_view_one) 
    UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM lecturercandidate_view_two) 
	UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM lecturercandidate_view_three);
	
	
CREATE TEMP TABLE lecturercandidate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, personname, ledge AS endpoint FROM lecturercandidate_view_u) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, personname, redge AS endpoint FROM lecturercandidate_view_u);  


CREATE TEMP TABLE lecturercandidate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM lecturercandidate_edges;

CREATE TEMP TABLE lecturercandidate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM lecturercandidate_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE lecturercandidate_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM lecturercandidate_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;


--  Lecturer(x) :- PublicationAuthor(y,x) Until_(0,2] LecturerCandidate(x)

CREATE TEMP TABLE publicationauthor_intersects_lecturercandidate AS
    SELECT personname, ledge, lendpointtype, redge, rendpointtype, publicationauthorledge, publicationauthorredge  
	FROM (
		SELECT publicationauthor_edges_star.personname,
	       greatest(publicationauthor_edges_star.ledge, lecturercandidate_edges_star.ledge) AS ledge,
	       least(publicationauthor_edges_star.redge, lecturercandidate_edges_star.redge) AS redge,
		   CASE
			   WHEN lecturercandidate_edges_star.ledge = greatest(publicationauthor_edges_star.ledge, lecturercandidate_edges_star.ledge) AND lecturercandidate_edges_star.lendpointtype = 3 THEN 3
			   ELSE 1
		   END AS lendpointtype,
		   CASE
		       WHEN lecturercandidate_edges_star.redge = least(publicationauthor_edges_star.redge, lecturercandidate_edges_star.redge) AND lecturercandidate_edges_star.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype, 
		   publicationauthor_edges_star.ledge AS publicationauthorledge, 
		   publicationauthor_edges_star.redge AS publicationauthorredge 
        FROM publicationauthor_edges_star, lecturercandidate_edges_star
        WHERE greatest(publicationauthor_edges_star.ledge, lecturercandidate_edges_star.ledge) <= least(publicationauthor_edges_star.redge, lecturercandidate_edges_star.redge)
	          AND
		      publicationauthor_edges_star.personname = lecturercandidate_edges_star.personname) AS innerTable 
	WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE publicationauthor_until_zero_two_lecturercandidate_pre AS 
    SELECT publicationauthor_intersects_lecturercandidate.personname, 
  	    greatest(publicationauthor_intersects_lecturercandidate.ledge - 2, publicationauthor_intersects_lecturercandidate.publicationauthorledge) AS ledge, 
  		least(publicationauthor_intersects_lecturercandidate.redge, publicationauthor_intersects_lecturercandidate.publicationauthorredge) AS redge, 
  		CASE 
  		    WHEN publicationauthor_intersects_lecturercandidate.lendpointtype = 3 AND publicationauthor_intersects_lecturercandidate.ledge - 2 >= publicationauthor_intersects_lecturercandidate.publicationauthorledge THEN 3 
  			ELSE 1
  		END AS lendpointtype, 
  		CASE 
  		    WHEN publicationauthor_intersects_lecturercandidate.redge <= publicationauthor_intersects_lecturercandidate.publicationauthorredge THEN 2 
  			ELSE 4
  		END AS rendpointtype 
  	FROM publicationauthor_intersects_lecturercandidate  
	WHERE greatest(publicationauthor_intersects_lecturercandidate.ledge - 2, publicationauthor_intersects_lecturercandidate.publicationauthorledge) <= least(publicationauthor_intersects_lecturercandidate.redge, publicationauthor_intersects_lecturercandidate.publicationauthorredge);


CREATE TEMP TABLE lecturer_view_one AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM publicationauthor_until_zero_two_lecturercandidate_pre 
	WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


--  Lecturer(x) :- boxplus_[1,5] LecturerCandidate(x)

CREATE TEMP TABLE lecturer_view_two AS 
    SELECT personname, (ledge-1) AS ledge, lendpointtype, (redge-5) AS redge, rendpointtype 
	FROM lecturercandidate_edges_star WHERE ledge - 1 < redge - 5 OR (ledge - 1 = redge - 5 AND lendpointtype = 1 AND rendpointtype = 4);


--  Coalesce lecturer

CREATE TEMP TABLE lecturer_view_u AS 
    (SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM lecturer_view_one) 
    UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM lecturer_view_two);


CREATE TEMP TABLE lecturer_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, personname, ledge AS endpoint FROM lecturer_view_u) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, personname, redge AS endpoint FROM lecturer_view_u) 
    UNION ALL 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS personname, left_val AS endpoint FROM lecturer) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS personname, right_val AS endpoint FROM lecturer);


CREATE TEMP TABLE lecturer_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM lecturer_edges;

CREATE TEMP TABLE lecturer_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM lecturer_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE lecturer_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM lecturer_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;





--  AssistantProfessorCandidate(x) :- diamondminus_[1,3] Lecturer(x)

CREATE TEMP TABLE assistantprofessorcandidate_view_one AS 
    SELECT personname, (ledge+1) AS ledge, lendpointtype, (redge+3) AS redge, rendpointtype FROM lecturer_edges_star;

--  AssistantProfessorCandidate(x) :- boxminus_[1,2] LecturerCandidate(x), diamondplus_[0,3] PublicationAuthor(z,x)

CREATE TEMP TABLE boxminus_one_two_lecturercandidate AS 
    SELECT personname, (ledge+2) AS ledge, lendpointtype, (redge+1) AS redge, rendpointtype 
	FROM lecturercandidate_edges_star WHERE ledge+2 < redge+1 OR (ledge+2 = redge+1 AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE diamondplus_zero_three_publicationauthor AS 
    SELECT pubname, personname, (ledge-3) AS ledge, lendpointtype, redge, rendpointtype FROM publicationauthor_edges_star;

CREATE TEMP TABLE assistantprofessorcandidate_view_two_pre AS 
    SELECT boxminus_one_two_lecturercandidate.personname, 
	       greatest(boxminus_one_two_lecturercandidate.ledge, diamondplus_zero_three_publicationauthor.ledge) AS ledge, 
	       least(boxminus_one_two_lecturercandidate.redge, diamondplus_zero_three_publicationauthor.redge) AS redge, 
		   CASE 
		       WHEN boxminus_one_two_lecturercandidate.ledge = greatest(boxminus_one_two_lecturercandidate.ledge, diamondplus_zero_three_publicationauthor.ledge) AND boxminus_one_two_lecturercandidate.lendpointtype = 3 THEN 3 
			   WHEN diamondplus_zero_three_publicationauthor.ledge = greatest(boxminus_one_two_lecturercandidate.ledge, diamondplus_zero_three_publicationauthor.ledge) AND diamondplus_zero_three_publicationauthor.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN boxminus_one_two_lecturercandidate.redge = least(boxminus_one_two_lecturercandidate.redge, diamondplus_zero_three_publicationauthor.redge) AND boxminus_one_two_lecturercandidate.rendpointtype = 2 THEN 2
		       WHEN diamondplus_zero_three_publicationauthor.redge = least(boxminus_one_two_lecturercandidate.redge, diamondplus_zero_three_publicationauthor.redge) AND diamondplus_zero_three_publicationauthor.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM boxminus_one_two_lecturercandidate, diamondplus_zero_three_publicationauthor  
    WHERE greatest(boxminus_one_two_lecturercandidate.ledge, diamondplus_zero_three_publicationauthor.ledge) <= least(boxminus_one_two_lecturercandidate.redge, diamondplus_zero_three_publicationauthor.redge) 
	      AND 
		  boxminus_one_two_lecturercandidate.personname = diamondplus_zero_three_publicationauthor.personname;

CREATE TEMP TABLE assistantprofessorcandidate_view_two AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM assistantprofessorcandidate_view_two_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


--  AssistantProfessorCandidate(x) :- boxminus_[1,2] LecturerCandidate(x), diamondminus_[0,3] DoctoralDegreeFrom(x,y)

CREATE TEMP TABLE doctoraldegreefrom_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS personname, entity[2] AS orgname, left_val AS endpoint FROM doctoraldegreefrom) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS personname, entity[2] AS orgname, right_val AS endpoint FROM doctoraldegreefrom);

CREATE TEMP TABLE doctoraldegreefrom_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname, orgname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname, orgname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname, orgname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname, orgname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname, orgname FROM doctoraldegreefrom_edges;

CREATE TEMP TABLE doctoraldegreefrom_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname, orgname FROM doctoraldegreefrom_edges_stepone 
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE doctoraldegreefrom_edges_star AS 
    SELECT personname, orgname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, orgname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname, orgname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname, orgname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM doctoraldegreefrom_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE diamondminus_zero_three_doctoraldegreefrom AS 
    SELECT personname, orgname, ledge, lendpointtype, (redge+3) AS redge, rendpointtype FROM doctoraldegreefrom_edges_star;

CREATE TEMP TABLE assistantprofessorcandidate_view_three_pre AS 
    SELECT boxminus_one_two_lecturercandidate.personname, 
	       greatest(boxminus_one_two_lecturercandidate.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge) AS ledge, 
	       least(boxminus_one_two_lecturercandidate.redge, diamondminus_zero_three_doctoraldegreefrom.redge) AS redge, 
		   CASE 
		       WHEN boxminus_one_two_lecturercandidate.ledge = greatest(boxminus_one_two_lecturercandidate.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge) AND boxminus_one_two_lecturercandidate.lendpointtype = 3 THEN 3 
			   WHEN diamondminus_zero_three_doctoraldegreefrom.ledge = greatest(boxminus_one_two_lecturercandidate.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge) AND diamondminus_zero_three_doctoraldegreefrom.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN boxminus_one_two_lecturercandidate.redge = least(boxminus_one_two_lecturercandidate.redge, diamondminus_zero_three_doctoraldegreefrom.redge) AND boxminus_one_two_lecturercandidate.rendpointtype = 2 THEN 2
		       WHEN diamondminus_zero_three_doctoraldegreefrom.redge = least(boxminus_one_two_lecturercandidate.redge, diamondminus_zero_three_doctoraldegreefrom.redge) AND diamondminus_zero_three_doctoraldegreefrom.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM boxminus_one_two_lecturercandidate, diamondminus_zero_three_doctoraldegreefrom   
    WHERE greatest(boxminus_one_two_lecturercandidate.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge) <= least(boxminus_one_two_lecturercandidate.redge, diamondminus_zero_three_doctoraldegreefrom.redge) 
	      AND 
		  boxminus_one_two_lecturercandidate.personname = diamondminus_zero_three_doctoraldegreefrom.personname;

CREATE TEMP TABLE assistantprofessorcandidate_view_three AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM assistantprofessorcandidate_view_three_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);

--  Coalesce assistantprofessorcandidate

CREATE TEMP TABLE assistantprofessorcandidate_view_u AS 
    (SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM assistantprofessorcandidate_view_one) 
    UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM assistantprofessorcandidate_view_two) 
	UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM assistantprofessorcandidate_view_three);


CREATE TEMP TABLE assistantprofessorcandidate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, personname, ledge AS endpoint FROM assistantprofessorcandidate_view_u) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, personname, redge AS endpoint FROM assistantprofessorcandidate_view_u);


CREATE TEMP TABLE assistantprofessorcandidate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM assistantprofessorcandidate_edges;

CREATE TEMP TABLE assistantprofessorcandidate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM assistantprofessorcandidate_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE assistantprofessorcandidate_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM assistantprofessorcandidate_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

--  AssociateProfessorCandidate(x) :- boxminus_[1,3] Lecturer(x), diamondminus_[0,3] DoctoralDegreeFrom(x,y), PublicationAuthor(z,x)

CREATE TEMP TABLE boxminus_one_three_lecturer AS 
    SELECT personname, (ledge+3) AS ledge, lendpointtype, (redge+1) AS redge, rendpointtype 
	FROM lecturer_edges_star WHERE ledge+3 < redge+1 OR (ledge+3 = redge+1 AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE associateprofessorcandidate_view_one_pre AS 
    SELECT boxminus_one_three_lecturer.personname, 
	       greatest(boxminus_one_three_lecturer.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge, publicationauthor_edges_star.ledge) AS ledge, 
	       least(boxminus_one_three_lecturer.redge, diamondminus_zero_three_doctoraldegreefrom.redge, publicationauthor_edges_star.redge) AS redge, 
		   CASE 
		       WHEN boxminus_one_three_lecturer.ledge = greatest(boxminus_one_three_lecturer.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge, publicationauthor_edges_star.ledge) AND boxminus_one_three_lecturer.lendpointtype = 3 THEN 3 
			   WHEN diamondminus_zero_three_doctoraldegreefrom.ledge = greatest(boxminus_one_three_lecturer.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge, publicationauthor_edges_star.ledge) AND diamondminus_zero_three_doctoraldegreefrom.lendpointtype = 3 THEN 3 
			   WHEN publicationauthor_edges_star.ledge = greatest(boxminus_one_three_lecturer.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge, publicationauthor_edges_star.ledge) AND publicationauthor_edges_star.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN boxminus_one_three_lecturer.redge = least(boxminus_one_three_lecturer.redge, diamondminus_zero_three_doctoraldegreefrom.redge, publicationauthor_edges_star.redge) AND boxminus_one_three_lecturer.rendpointtype = 2 THEN 2
		       WHEN diamondminus_zero_three_doctoraldegreefrom.redge = least(boxminus_one_three_lecturer.redge, diamondminus_zero_three_doctoraldegreefrom.redge, publicationauthor_edges_star.redge) AND diamondminus_zero_three_doctoraldegreefrom.rendpointtype = 2 THEN 2 
			   WHEN publicationauthor_edges_star.redge = least(boxminus_one_three_lecturer.redge, diamondminus_zero_three_doctoraldegreefrom.redge, publicationauthor_edges_star.redge) AND publicationauthor_edges_star.rendpointtype = 2 THEN 2 
		       ELSE 4
		   END AS rendpointtype
    FROM boxminus_one_three_lecturer, diamondminus_zero_three_doctoraldegreefrom, publicationauthor_edges_star   
    WHERE greatest(boxminus_one_three_lecturer.ledge, diamondminus_zero_three_doctoraldegreefrom.ledge, publicationauthor_edges_star.ledge) <= least(boxminus_one_three_lecturer.redge, diamondminus_zero_three_doctoraldegreefrom.redge, publicationauthor_edges_star.redge)  
	      AND 
		  boxminus_one_three_lecturer.personname = diamondminus_zero_three_doctoraldegreefrom.personname 
		  AND 
		  diamondminus_zero_three_doctoraldegreefrom.personname = publicationauthor_edges_star.personname;

CREATE TEMP TABLE associateprofessorcandidate_view_one AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM associateprofessorcandidate_view_one_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4); 

--  AssociateProfessorCandidate(x) :- boxminus_[1,5] AssistantProfessorCandidate(x)

CREATE TEMP TABLE associateprofessorcandidate_view_two AS 
    SELECT personname, (ledge+5) AS ledge, lendpointtype, (redge+1) AS redge, rendpointtype 
	FROM assistantprofessorcandidate_edges_star WHERE ledge+5 < redge+1 OR (ledge+5 = redge+1 AND lendpointtype = 1 AND rendpointtype = 4);

--  AssociateProfessorCandidate(x) :- boxminus_[1,3] AssistantProfessor(x)

CREATE TEMP TABLE assistantprofessor_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS personname, left_val AS endpoint FROM assistantprofessor) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS personname, right_val AS endpoint FROM assistantprofessor);


CREATE TEMP TABLE assistantprofessor_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM assistantprofessor_edges;

CREATE TEMP TABLE assistantprofessor_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM assistantprofessor_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE assistantprofessor_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM assistantprofessor_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE associateprofessorcandidate_view_three AS 
    SELECT personname, (ledge+3) AS ledge, lendpointtype, (redge+1) AS redge, rendpointtype 
	FROM assistantprofessor_edges_star WHERE ledge+3 < redge+1 OR (ledge+3 = redge+1 AND lendpointtype = 1 AND rendpointtype = 4);

--  AssociateProfessorCandidate(x) :- boxminus_[1,2] AssistantProfessorCandidate(x), DoctoralDegreeFrom(x,y)

CREATE TEMP TABLE boxminus_one_two_assistantprofessorcandidate AS 
    SELECT personname, (ledge+2) AS ledge, lendpointtype, (redge+1) AS redge, rendpointtype 
    FROM assistantprofessorcandidate_edges_star WHERE ledge+2 < redge+1 OR (ledge+2 = redge+1 AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE associateprofessorcandidate_view_four_pre AS 
    SELECT boxminus_one_two_assistantprofessorcandidate.personname, 
	       greatest(boxminus_one_two_assistantprofessorcandidate.ledge, doctoraldegreefrom_edges_star.ledge) AS ledge, 
	       least(boxminus_one_two_assistantprofessorcandidate.redge, doctoraldegreefrom_edges_star.redge) AS redge, 
		   CASE 
		       WHEN boxminus_one_two_assistantprofessorcandidate.ledge = greatest(boxminus_one_two_assistantprofessorcandidate.ledge, doctoraldegreefrom_edges_star.ledge) AND boxminus_one_two_assistantprofessorcandidate.lendpointtype = 3 THEN 3 
			   WHEN doctoraldegreefrom_edges_star.ledge = greatest(boxminus_one_two_assistantprofessorcandidate.ledge, doctoraldegreefrom_edges_star.ledge) AND doctoraldegreefrom_edges_star.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN boxminus_one_two_assistantprofessorcandidate.redge = least(boxminus_one_two_assistantprofessorcandidate.redge, doctoraldegreefrom_edges_star.redge) AND boxminus_one_two_assistantprofessorcandidate.rendpointtype = 2 THEN 2
		       WHEN doctoraldegreefrom_edges_star.redge = least(boxminus_one_two_assistantprofessorcandidate.redge, doctoraldegreefrom_edges_star.redge) AND doctoraldegreefrom_edges_star.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM boxminus_one_two_assistantprofessorcandidate, doctoraldegreefrom_edges_star   
    WHERE greatest(boxminus_one_two_assistantprofessorcandidate.ledge, doctoraldegreefrom_edges_star.ledge) <= least(boxminus_one_two_assistantprofessorcandidate.redge, doctoraldegreefrom_edges_star.redge) 
	      AND 
		  boxminus_one_two_assistantprofessorcandidate.personname = doctoraldegreefrom_edges_star.personname;

CREATE TEMP TABLE associateprofessorcandidate_view_four AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM associateprofessorcandidate_view_four_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);

--  AssociateProfessorCandidate(x) :- boxplus_[1,3] AssistantProfessor(x)

CREATE TEMP TABLE associateprofessorcandidate_view_five AS 
    SELECT personname, (ledge-1) AS ledge, lendpointtype, (redge-3) AS redge, rendpointtype 
	FROM assistantprofessor_edges_star WHERE ledge - 1 < redge - 3 OR (ledge - 1 = redge - 3 AND lendpointtype = 1 AND rendpointtype = 4);

--  Coalesce associateprofessorcandidate

CREATE TEMP TABLE associateprofessorcandidate_view_u AS 
    (SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM associateprofessorcandidate_view_one) 
    UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM associateprofessorcandidate_view_two) 
	UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM associateprofessorcandidate_view_three) 
	UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM associateprofessorcandidate_view_four) 
	UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM associateprofessorcandidate_view_five);


CREATE TEMP TABLE associateprofessorcandidate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, personname, ledge AS endpoint FROM associateprofessorcandidate_view_u) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, personname, redge AS endpoint FROM associateprofessorcandidate_view_u);


CREATE TEMP TABLE associateprofessorcandidate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM associateprofessorcandidate_edges;

CREATE TEMP TABLE associateprofessorcandidate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM associateprofessorcandidate_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE associateprofessorcandidate_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM associateprofessorcandidate_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;


--  AssociateProfessor(x) :- diamondminus_[1,2] AssociateProfessorCandidate(x)

CREATE TEMP TABLE associateprofessor_view_one AS 
    SELECT personname, (ledge+1) AS ledge, lendpointtype, (redge+2) AS redge, rendpointtype FROM associateprofessorcandidate_edges_star;

CREATE TEMP TABLE associateprofessor_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, personname, ledge AS endpoint FROM associateprofessor_view_one) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, personname, redge AS endpoint FROM associateprofessor_view_one) 
    UNION ALL 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS personname, left_val AS endpoint FROM associateprofessor) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS personname, right_val AS endpoint FROM associateprofessor);


CREATE TEMP TABLE associateprofessor_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM associateprofessor_edges;

CREATE TEMP TABLE associateprofessor_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM associateprofessor_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE associateprofessor_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM associateprofessor_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

--  FullProfessorCandidate(x) :- boxplus_[1,2]AssociateProfessorCandidate(x), diamondminus_[0,3]publicationauthor(y,x)

CREATE TEMP TABLE boxplus_one_two_associateprofessorcandidate AS 
    SELECT personname, (ledge-1) AS ledge, lendpointtype, (redge-2) AS redge, rendpointtype 
	FROM associateprofessorcandidate_edges_star WHERE ledge - 1 < redge - 2 OR (ledge - 1 = redge - 2 AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE diamondminus_zero_three_publicationauthor AS 
    SELECT pubname, personname, ledge, lendpointtype, (redge+3) AS redge, rendpointtype 
	FROM publicationauthor_edges_star;
	
CREATE TEMP TABLE fullprofessorcandidate_view_one_pre AS 
    SELECT boxplus_one_two_associateprofessorcandidate.personname, 
	       greatest(boxplus_one_two_associateprofessorcandidate.ledge, diamondminus_zero_three_publicationauthor.ledge) AS ledge, 
	       least(boxplus_one_two_associateprofessorcandidate.redge, diamondminus_zero_three_publicationauthor.redge) AS redge, 
		   CASE 
		       WHEN boxplus_one_two_associateprofessorcandidate.ledge = greatest(boxplus_one_two_associateprofessorcandidate.ledge, diamondminus_zero_three_publicationauthor.ledge) AND boxplus_one_two_associateprofessorcandidate.lendpointtype = 3 THEN 3 
			   WHEN diamondminus_zero_three_publicationauthor.ledge = greatest(boxplus_one_two_associateprofessorcandidate.ledge, diamondminus_zero_three_publicationauthor.ledge) AND diamondminus_zero_three_publicationauthor.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN boxplus_one_two_associateprofessorcandidate.redge = least(boxplus_one_two_associateprofessorcandidate.redge, diamondminus_zero_three_publicationauthor.redge) AND boxplus_one_two_associateprofessorcandidate.rendpointtype = 2 THEN 2
		       WHEN diamondminus_zero_three_publicationauthor.redge = least(boxplus_one_two_associateprofessorcandidate.redge, diamondminus_zero_three_publicationauthor.redge) AND diamondminus_zero_three_publicationauthor.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM boxplus_one_two_associateprofessorcandidate, diamondminus_zero_three_publicationauthor   
    WHERE greatest(boxplus_one_two_associateprofessorcandidate.ledge, diamondminus_zero_three_publicationauthor.ledge) <= least(boxplus_one_two_associateprofessorcandidate.redge, diamondminus_zero_three_publicationauthor.redge) 
	      AND 
		  boxplus_one_two_associateprofessorcandidate.personname = diamondminus_zero_three_publicationauthor.personname;

CREATE TEMP TABLE fullprofessorcandidate_view_one AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM fullprofessorcandidate_view_one_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


--  FullProfessorCandidate(x) :- boxminus_[1,2]AssociateProfessor(x), diamondminus_[0,3]publicationauthor(y,x)

CREATE TEMP TABLE boxminus_one_two_associateprofessor AS 
    SELECT personname, (ledge+2) AS ledge, lendpointtype, (redge+1) AS redge, rendpointtype 
	FROM associateprofessor_edges_star WHERE ledge + 2 < redge + 1 OR (ledge + 2 = redge + 1 AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE fullprofessorcandidate_view_two_pre AS 
    SELECT boxminus_one_two_associateprofessor.personname, 
	       greatest(boxminus_one_two_associateprofessor.ledge, diamondminus_zero_three_publicationauthor.ledge) AS ledge, 
	       least(boxminus_one_two_associateprofessor.redge, diamondminus_zero_three_publicationauthor.redge) AS redge, 
		   CASE 
		       WHEN boxminus_one_two_associateprofessor.ledge = greatest(boxminus_one_two_associateprofessor.ledge, diamondminus_zero_three_publicationauthor.ledge) AND boxminus_one_two_associateprofessor.lendpointtype = 3 THEN 3 
			   WHEN diamondminus_zero_three_publicationauthor.ledge = greatest(boxminus_one_two_associateprofessor.ledge, diamondminus_zero_three_publicationauthor.ledge) AND diamondminus_zero_three_publicationauthor.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN boxminus_one_two_associateprofessor.redge = least(boxminus_one_two_associateprofessor.redge, diamondminus_zero_three_publicationauthor.redge) AND boxminus_one_two_associateprofessor.rendpointtype = 2 THEN 2
		       WHEN diamondminus_zero_three_publicationauthor.redge = least(boxminus_one_two_associateprofessor.redge, diamondminus_zero_three_publicationauthor.redge) AND diamondminus_zero_three_publicationauthor.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM boxminus_one_two_associateprofessor, diamondminus_zero_three_publicationauthor   
    WHERE greatest(boxminus_one_two_associateprofessor.ledge, diamondminus_zero_three_publicationauthor.ledge) <= least(boxminus_one_two_associateprofessor.redge, diamondminus_zero_three_publicationauthor.redge) 
	      AND 
		  boxminus_one_two_associateprofessor.personname = diamondminus_zero_three_publicationauthor.personname;

CREATE TEMP TABLE fullprofessorcandidate_view_two AS 
    SELECT personname, ledge, lendpointtype, redge, rendpointtype FROM fullprofessorcandidate_view_two_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


-- Coalesce FullProfessorCandidate

CREATE TEMP TABLE fullprofessorcandidate_view_u AS 
    (SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM fullprofessorcandidate_view_one) 
    UNION 
	(SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM fullprofessorcandidate_view_two);


CREATE TEMP TABLE fullprofessorcandidate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, personname, ledge AS endpoint FROM fullprofessorcandidate_view_u) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, personname, redge AS endpoint FROM fullprofessorcandidate_view_u);


CREATE TEMP TABLE fullprofessorcandidate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, personname FROM fullprofessorcandidate_edges;

CREATE TEMP TABLE fullprofessorcandidate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, personname FROM fullprofessorcandidate_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE fullprofessorcandidate_edges_star AS 
    SELECT personname, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT personname, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY personname ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM fullprofessorcandidate_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

























































