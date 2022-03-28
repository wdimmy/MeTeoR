-- Boxminus[0,1]ExcessiveHeat(X):-Boxminus[0,1]TempAbove24(X), Diamondminus[0,1]TempAbove41(X)

CREATE TEMP TABLE tempabove24_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS stationid, left_val AS endpoint FROM tempabove24) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS stationid, right_val AS endpoint FROM tempabove24);

CREATE TEMP TABLE tempabove24_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, stationid FROM tempabove24_edges;

CREATE TEMP TABLE tempabove24_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, stationid FROM tempabove24_edges_stepone 
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE tempabove24_edges_star AS 
    SELECT stationid, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT stationid, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM tempabove24_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE boxminus_zero_one_tempabove24 AS 
    SELECT stationid, (ledge+1) AS ledge, lendpointtype, redge, rendpointtype FROM tempabove24_edges_star WHERE ledge+1 < redge OR (ledge+1 = redge AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE tempabove41_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, CASE WHEN left_open=FALSE THEN 1 ELSE 3 END AS endpointtype, entity[1] AS stationid, left_val AS endpoint FROM tempabove41) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, CASE WHEN right_open=TRUE THEN 2 ELSE 4 END AS endpointtype, entity[1] AS stationid, right_val AS endpoint FROM tempabove41);

CREATE TEMP TABLE tempabove41_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
	       (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
		   (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
		   (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
		   endpoint, endpointtype, stationid FROM tempabove41_edges;

CREATE TEMP TABLE tempabove41_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
	       COALESCE (curcntright, 0) AS curcntright, 
		   COALESCE (prvcntleft, 0) AS prvcntleft, 
		   COALESCE (prvcntright, 0) AS prvcntright, 
		   endpoint, endpointtype, stationid FROM tempabove41_edges_stepone 
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE tempabove41_edges_star AS 
    SELECT stationid, ledge, redge, lendpointtype, rendpointtype FROM 
	    (SELECT stationid, curcntleft, curcntright, 
			    (MAX(endpoint) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
		        (MAX(endpointtype) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
				endpoint AS redge, 
				endpointtype AS rendpointtype 
		 FROM tempabove41_edges_steptwo) AS interTable 
	WHERE curcntleft = curcntright;

CREATE TEMP TABLE diamondminus_zero_one_tempabove41 AS 
    SELECT stationid, ledge, lendpointtype, (redge + 1) AS redge, rendpointtype FROM tempabove41_edges_star;


CREATE TEMP TABLE excessiveheatcandidate_view_pre AS 
    SELECT boxminus_zero_one_tempabove24.stationid, 
        greatest(boxminus_zero_one_tempabove24.ledge, diamondminus_zero_one_tempabove41.ledge) AS ledge, 
        least(boxminus_zero_one_tempabove24.redge, diamondminus_zero_one_tempabove41.redge) AS redge, 
	    CASE 
	        WHEN boxminus_zero_one_tempabove24.ledge = greatest(boxminus_zero_one_tempabove24.ledge, diamondminus_zero_one_tempabove41.ledge) AND boxminus_zero_one_tempabove24.lendpointtype = 3 THEN 3 
		    WHEN diamondminus_zero_one_tempabove41.ledge = greatest(boxminus_zero_one_tempabove24.ledge, diamondminus_zero_one_tempabove41.ledge) AND diamondminus_zero_one_tempabove41.lendpointtype = 3 THEN 3 
		    ELSE 1 
	    END AS lendpointtype, 
	    CASE
	        WHEN boxminus_zero_one_tempabove24.redge = least(boxminus_zero_one_tempabove24.redge, diamondminus_zero_one_tempabove41.redge) AND boxminus_zero_one_tempabove24.rendpointtype = 2 THEN 2
	        WHEN diamondminus_zero_one_tempabove41.redge = least(boxminus_zero_one_tempabove24.redge, diamondminus_zero_one_tempabove41.redge) AND diamondminus_zero_one_tempabove41.rendpointtype = 2 THEN 2
	        ELSE 4
	    END AS rendpointtype
    FROM boxminus_zero_one_tempabove24, diamondminus_zero_one_tempabove41 
    WHERE boxminus_zero_one_tempabove24.stationid = diamondminus_zero_one_tempabove41.stationid 
          AND 
          greatest(boxminus_zero_one_tempabove24.ledge, diamondminus_zero_one_tempabove41.ledge) <= least(boxminus_zero_one_tempabove24.redge, diamondminus_zero_one_tempabove41.redge);
		  
CREATE TEMP TABLE excessiveheatcandidate_view AS 
    SELECT stationid, ledge, lendpointtype, redge, rendpointtype FROM excessiveheatcandidate_view_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);


CREATE TEMP TABLE excessiveheatcandidate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, stationid, ledge AS endpoint FROM excessiveheatcandidate_view) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, stationid, redge AS endpoint FROM excessiveheatcandidate_view);


CREATE TEMP TABLE excessiveheatcandidate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
        (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
        (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
        (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
        endpoint, endpointtype, stationid FROM excessiveheatcandidate_edges;

CREATE TEMP TABLE excessiveheatcandidate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
        COALESCE (curcntright, 0) AS curcntright, 
        COALESCE (prvcntleft, 0) AS prvcntleft, 
        COALESCE (prvcntright, 0) AS prvcntright, 
        endpoint, endpointtype, stationid FROM excessiveheatcandidate_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE excessiveheatcandidate_edges_star AS 
    SELECT stationid, ledge, redge, lendpointtype, rendpointtype FROM 
        (SELECT stationid, curcntleft, curcntright, 
            (MAX(endpoint) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
            (MAX(endpointtype) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
            endpoint AS redge, 
            endpointtype AS rendpointtype 
        FROM excessiveheatcandidate_edges_steptwo) AS interTable 
    WHERE curcntleft = curcntright;

CREATE TEMP TABLE excessiveheat_view AS 
    SELECT stationid, (ledge-1) AS ledge, lendpointtype, redge, rendpointtype FROM excessiveheatcandidate_edges_star;

CREATE TEMP TABLE excessiveheat_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, stationid, ledge AS endpoint FROM excessiveheat_view) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, stationid, redge AS endpoint FROM excessiveheat_view);


CREATE TEMP TABLE excessiveheat_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
        (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
        (SUM(ifleft) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
        (SUM(ifright) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
        endpoint, endpointtype, stationid FROM excessiveheat_edges;

CREATE TEMP TABLE excessiveheat_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
        COALESCE (curcntright, 0) AS curcntright, 
        COALESCE (prvcntleft, 0) AS prvcntleft, 
        COALESCE (prvcntright, 0) AS prvcntright, 
        endpoint, endpointtype, stationid FROM excessiveheat_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE excessiveheat_edges_star AS 
    SELECT stationid, ledge, redge, lendpointtype, rendpointtype FROM 
        (SELECT stationid, curcntleft, curcntright, 
            (MAX(endpoint) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
            (MAX(endpointtype) OVER (PARTITION BY stationid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
            endpoint AS redge, 
            endpointtype AS rendpointtype 
        FROM excessiveheat_edges_steptwo) AS interTable 
    WHERE curcntleft = curcntright;

-- HeatAffectedState(X):-LocatedInState(Y,X), ExcessiveHeat(Y)
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

CREATE TEMP TABLE heataffectedstate_view_pre AS 
    SELECT locatedinstate_edges_star.stateid, 
	       greatest(locatedinstate_edges_star.ledge, excessiveheat_edges_star.ledge) AS ledge, 
	       least(locatedinstate_edges_star.redge, excessiveheat_edges_star.redge) AS redge, 
		   CASE 
		       WHEN locatedinstate_edges_star.ledge = greatest(locatedinstate_edges_star.ledge, excessiveheat_edges_star.ledge) AND locatedinstate_edges_star.lendpointtype = 3 THEN 3 
			   WHEN excessiveheat_edges_star.ledge = greatest(locatedinstate_edges_star.ledge, excessiveheat_edges_star.ledge) AND excessiveheat_edges_star.lendpointtype = 3 THEN 3 
			   ELSE 1 
		   END AS lendpointtype, 
		   CASE
		       WHEN locatedinstate_edges_star.redge = least(locatedinstate_edges_star.redge, excessiveheat_edges_star.redge) AND locatedinstate_edges_star.rendpointtype = 2 THEN 2
		       WHEN excessiveheat_edges_star.redge = least(locatedinstate_edges_star.redge, excessiveheat_edges_star.redge) AND excessiveheat_edges_star.rendpointtype = 2 THEN 2
		       ELSE 4
		   END AS rendpointtype
    FROM locatedinstate_edges_star, excessiveheat_edges_star 
    WHERE locatedinstate_edges_star.stationid = excessiveheat_edges_star.stationid 
	      AND 
	      greatest(locatedinstate_edges_star.ledge, excessiveheat_edges_star.ledge) <= least(locatedinstate_edges_star.redge, excessiveheat_edges_star.redge);
		  
CREATE TEMP TABLE heataffectedstate_view AS 
    SELECT stateid, ledge, lendpointtype, redge, rendpointtype FROM heataffectedstate_view_pre WHERE ledge < redge OR (ledge = redge AND lendpointtype = 1 AND rendpointtype = 4);

CREATE TEMP TABLE heataffectedstate_edges AS 
    (SELECT 1 AS ifleft, 0 AS ifright, lendpointtype AS endpointtype, stateid, ledge AS endpoint FROM heataffectedstate_view) 
    UNION ALL 
    (SELECT 0 AS ifleft, 1 AS ifright, rendpointtype AS endpointtype, stateid, redge AS endpoint FROM heataffectedstate_view);


CREATE TEMP TABLE heataffectedstate_edges_stepone AS 
    SELECT (SUM(ifleft) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntleft, 
           (SUM(ifright) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS UNBOUNDED PRECEDING)) AS curcntright, 
           (SUM(ifleft) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntleft, 
           (SUM(ifright) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN UNBOUNDED PRECEDING AND 1 PRECEDING)) AS prvcntright, 
           endpoint, endpointtype, stateid FROM heataffectedstate_edges;

CREATE TEMP TABLE heataffectedstate_edges_steptwo AS 
    SELECT COALESCE (curcntleft, 0) AS curcntleft, 
           COALESCE (curcntright, 0) AS curcntright, 
           COALESCE (prvcntleft, 0) AS prvcntleft, 
           COALESCE (prvcntright, 0) AS prvcntright, 
           endpoint, endpointtype, stateid FROM heataffectedstate_edges_stepone  
    WHERE COALESCE (curcntleft, 0) = COALESCE (curcntright, 0) OR COALESCE (prvcntleft, 0) = COALESCE (prvcntright, 0);

CREATE TEMP TABLE heataffectedstate_edges_star AS 
    SELECT stateid, ledge, redge, lendpointtype, rendpointtype FROM 
        (SELECT stateid, curcntleft, curcntright, 
                (MAX(endpoint) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS ledge, 
                (MAX(endpointtype) OVER (PARTITION BY stateid ORDER BY endpoint ASC, endpointtype ASC ROWS BETWEEN 1 PRECEDING AND 1 PRECEDING)) AS lendpointtype, 
                endpoint AS redge, 
                endpointtype AS rendpointtype 
         FROM heataffectedstate_edges_steptwo) AS interTable 
    WHERE curcntleft = curcntright;

