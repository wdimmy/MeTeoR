import logging


def get_min_max_rational(D):
    min_val = float("inf")
    max_val = float("-inf")
    for predicate in D:
        for entity in D[predicate]:
            for intv in D[predicate][entity]:
                min_val = min(min_val, intv.left_value)
                max_val = max(max_val, intv.right_value)
    return min_val, max_val


def print_dataset(D):
    """
    Print all facts in D, the outputing form
    Args:
        D (a dictionary object):

    Returns:

    """
    for predicate in D:
        for entity, intervals in D[predicate].items():
            for interval in intervals:
                if len(entity) == 1 and entity[0].name == "nan":
                     print(predicate+"@"+str(interval))
                else:
                    print(predicate + "(" + ",".join([item.name for item in entity]) + ")@" + str(interval))


def save_dataset_to_file(filename, D):
    """
       Print all facts in D, the outputing form
       Args:
           D (a dictionary object):

       Returns:

       """
    filewriter = open(filename, "w")
    for predicate in D:
        for entity, intervals in D[predicate].items():
            for interval in intervals:
                if len(entity) == 1 and entity[0].name == "nan":
                    filewriter(predicate + "@" + str(interval)+"\n")
                else:
                    filewriter.write(predicate + "(" + ",".join([item.name for item in entity]) + ")@" + str(interval)+"\n")

def return_dataset(D):
    """
    Print all facts in D, the outputing form
    Args:
        D (a dictionary object):

    Returns:

    """
    res = ""
    for predicate in D:
        if "TMP" in predicate:
            continue
        if type(D[predicate]) == list:
            for interval in D[predicate]:
                res += predicate+"@"+str(interval) +"<br/>"
        else:
            for entity, intervals in D[predicate].items():
                entity_name = ",".join([item.name for item in entity if item.name != "nan"])
                for interval in intervals:
                    if entity_name != "":
                       res += predicate+"("+ entity_name + ")@"+str(interval) + "<br/>"
                    else:
                        res += predicate + "@" + str(interval) + "<br/>"

    return res


def yield_dataset(D):
    """
    Print all facts in D, the outputing form
    Args:
        D (a dictionary object):

    Returns:

    """
    res = ""
    for predicate in D:
        if "TMP" in predicate:
            continue
        if type(D[predicate]) == list:
            for interval in D[predicate]:
                res += predicate+"@"+str(interval) +"<br/>"
        else:
            for entity, intervals in D[predicate].items():
                entity_name = ",".join([item.name for item in entity if item.name != "nan"])
                for interval in intervals:
                    if entity_name != "":
                       yield predicate+"("+ entity_name + ")@"+str(interval)
                    else:
                        yield predicate + "@" + str(interval)

    return res



def print_predicate(predicate, D, num=100000):
    """
    Print all fact with a specified predicate.
    Args:
        predicate (str):
        D (a dictionary object):

    Returns:

    """
    if predicate in D:
        cnt = 0
        if type(D[predicate]) == list:
            for interval in D[predicate]:
                cnt += 1
                logging.info(predicate + "@" + str(interval))
                if cnt > num:
                    break
        else:
            for entity, intervals in D[predicate].items():
                for interval in intervals:
                    cnt += 1
                    if cnt < num:
                        logging.info(predicate + "(" + ",".join([item.name for item in entity]) + ")@" + str(interval))

        logging.info("The total number of the predicate({}) is {}".format(predicate, cnt))

    else:
        print("{} does not exist in D!".format(predicate))


def save_predicate(predicate, D, outfilename="result.txt"):
    """
    Print all fact with a specified predicate.
    Args:
        predicate (str):
        D (a dictionary object):

    Returns:

    """
    with open(outfilename, "w") as file:
        if predicate in D:
            if type(D[predicate]) == list:
                for interval in D[predicate]:
                    file.write(predicate + "@" + str(interval))
                    file.write("\n")
            else:
                for entity, intervals in D[predicate].items():
                    for interval in intervals:
                        file.write(predicate + "(" + ",".join([item.name for item in entity]) + ")@" + str(interval))
                        file.write("\n")
        else:
            print("{} does not exist in D!".format(predicate))


def save_dataset(D, outfilename):
    with open(outfilename, "w") as file:
        for predicate in D:
            if type(D[predicate]) == list:
                for interval in D[predicate]:
                    file.write(predicate + "@" + str(interval))
                    file.write("\n")
            else:
                for entity, intervals in D[predicate].items():
                    for interval in intervals:
                        file.write(predicate + "(" + ",".join([item.name for item in entity]) + ")@" + str(interval))
                        file.write("\n")
