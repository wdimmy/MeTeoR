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

