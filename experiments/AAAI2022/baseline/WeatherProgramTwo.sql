-- Boxminus[0,1]heavywind(X):-Boxminus[0,1]heavywindforce(X)

CREATE TEMP TABLE heavywindforce_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS stationid, left_val AS endpoint FROM heavywindforce) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS stationid, right_val AS endpoint FROM heavywindforce);

CREATE TEMP TABLE heavywindforce_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, stationid FROM heavywindforce_edges;

CREATE TEMP TABLE heavywindforce_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, stationid FROM heavywindforce_edges_stepone 
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE heavywindforce_edges_star AS 
    SELECT stationid, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT stationid, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM heavywindforce_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE heavywindcandidate AS 
    SELECT stationid, (ledge+1) AS ledge, lendpointtype, redge, rendpointtype FROM heavywindforce_edges_star WHERE ledge+1 < redge OR (ledge+1 = redge AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE heavywind_edges_star AS 
    SELECT stationid, (ledge-1) AS ledge, lendpointtype, redge, rendpointtype FROM heavywindcandidate;

-- heavywindAffectedState(X):-LocatedInState(Y,X),heavywind(Y)

CREATE TEMP TABLE locatedinstate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS stationid, entity[2] AS stateid, left_val AS endpoint FROM locatedinstate) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS stationid, entity[2] AS stateid, right_val AS endpoint FROM locatedinstate);

CREATE TEMP TABLE locatedinstate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY stationid, stateid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY stationid, stateid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY stationid, stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY stationid, stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, stationid, stateid FROM locatedinstate_edges;

CREATE TEMP TABLE locatedinstate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, stationid, stateid FROM locatedinstate_edges_stepone 
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE locatedinstate_edges_star AS 
    SELECT stationid, stateid, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT stationid, stateid, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY stationid, stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY stationid, stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM locatedinstate_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE heavywindaffectedstate_view_pre AS 
    SELECT locatedinstate_edges_star.stateid, 
	       greatest(locatedinstate_edges_star.ledge, heavywind_edges_star.ledge) AS ledge, 
	       least(locatedinstate_edges_star.redge, heavywind_edges_star.redge) AS redge, 
		   CASE 
		       WHEN locatedinstate_edges_star.ledge = greatest(locatedinstate_edges_star.ledge, heavywind_edges_star.ledge) AND locatedinstate_edges_star.lendpointtype = 3 THEN 3 
			   WHEN heavywind_edges_star.ledge = greatest(locatedinstate_edges_star.ledge, heavywind_edges_star.ledge) AND heavywind_edges_star.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN locatedinstate_edges_star.redge = least(locatedinstate_edges_star.redge, heavywind_edges_star.redge) AND locatedinstate_edges_star.rendpointtype = 2 THEN 2
		       WHEN heavywind_edges_star.redge = least(locatedinstate_edges_star.redge, heavywind_edges_star.redge) AND heavywind_edges_star.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM locatedinstate_edges_star, heavywind_edges_star 
    WHERE locatedinstate_edges_star.stationid = heavywind_edges_star.stationid 
	      AND 
	      greatest(locatedinstate_edges_star.ledge, heavywind_edges_star.ledge) <= least(locatedinstate_edges_star.redge, heavywind_edges_star.redge);
		  
CREATE TEMP TABLE heavywindaffectedstate_view AS 
      SELECT stateid, ledge, lendpointtype, redge, rendpointtype FROM heavywindaffectedstate_view_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


CREATE TEMP TABLE heavywindaffectedstate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, stateid, ledge AS endpoint FROM heavywindaffectedstate_view) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, stateid, redge AS endpoint FROM heavywindaffectedstate_view);


CREATE TEMP TABLE heavywindaffectedstate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
           (SUM(ifright) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
           (SUM(ifleft) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
           (SUM(ifright) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
           endpoint, endpointtype, stateid FROM heavywindaffectedstate_edges;

CREATE TEMP TABLE heavywindaffectedstate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
           COALESCE (curcntright, 0) AS curcntright, 
           COALESCE (prvcntleft, 0) AS prvcntleft, 
           COALESCE (prvcntright, 0) AS prvcntright, 
           endpoint, endpointtype, stateid FROM heavywindaffectedstate_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE heavywindaffectedstate_edges_star AS 
    SELECT stateid, ledge, redge, lendpointtype, rendpointtype FROM 
        (SELECT stateid, curcntleft, curcntright, 
                (MAX(endpoint) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
                (MAX(endpointtype) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
                endpoint AS redge, 
                endpointtype AS rendpointtype 
         FROM heavywindaffectedstate_edges_steptwo) AS interTable 
    WHERE curcntleft = curcntright;







