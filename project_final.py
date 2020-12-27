#!/usr/bin/env python3

# PROJECT 5: DATA ANALYSIS 
# By: Nina Shenker-Tauris & Sofus Halkjær Wiisbye

import datetime
from datetime import date


# Preparing our data structure. Creating a list of dicts for the data to be put into.
def read_people_as_dict(file_name):
    people = []
    current_person = {}

    # Read in the file once
    try:
        with open('people.db', 'r') as file:
            line = True
            while line:
                line = file.readline()
                # Creating a dict for each individual person
                if line.strip() == '':
                    # Secures we do not create dict initial space, between file header and first entry 
                    if len(current_person) > 1:
                        people.append(current_person)
                    else:
                        continue
                    # Reset of current_person
                    current_person = { }
                # Skips header preceeded by #
                elif line[0] == '#':
                    continue
                else:
                    # Get key and value from line
                    split_line = line.split(': ')
                    key = split_line[0]
                    value = split_line[-1].rstrip('\n')
                    current_person[key] = value
                    # CPR key contains information of both age and gender as 'ddmmyy - xxxX'. X will determine gender, Odd=make/Even=female
                    if key == 'CPR':
                         current_person["Age"] = get_age_from_cpr(value)
                         current_person["Gender"] = get_gender_from_cpr(value)
                    elif key == 'Children':
                        # Extract first child age
                        children_cprs = value.split()
                        child_ages = [(get_age_from_cpr(x), x) for x in children_cprs]
                        first_child = max(child_ages)
                        # Find the age when they had first child
                        current_person['Parent age'] = current_person['Age'] - first_child[0]
                        # Extract first born chender
                        current_person["First child gender"] = get_gender_from_cpr(first_child[1])

    except IOError as error:
        print('File not found, reason:', str(error))

    return people


# To get an overview of the data in a table format
def print_people_as_table(people):
    # Create column headers and format spacing/dashed line
    column_order = ['CPR', 'Age', 'Gender', 'First name', 'Last name', 'Height', 'Weight', 'Blood type', 'Children']
    for value in column_order:
        formatted = " {0:16}".format(value)
        print(formatted, end="")
    print()

    print('-' * (len(column_order) + 1) * 15)
    # Add values for each column header
    for row in people:
        col_values = [row[col] for col in column_order if col in row]
        for value in col_values:
            formatted = " {0:<16}".format(value)
            print(formatted, end="")
        print()


# Defining our age groups
def bucket_age(ages):
    if ages <= 10:
        return "0-10"
    elif ages <= 20:
        return "11-20"
    elif ages <= 30:
        return "21-30"
    elif ages <= 40:
        return "31-40"
    elif ages <= 50:
        return "41-50"
    elif ages <= 60:
        return "51-60"
    elif ages <= 70:
        return "61-70"
    elif ages <= 80:
        return "71-80"
    elif ages <= 90:
        return "81-90"
    else:
        return "91+"


# With the date function we extract birthdate from CPR and calculate age in year 2000
def get_age_from_cpr(cpr):
    ddmmyy = cpr.split('-')[0]
    pydate = date(
        year=int(ddmmyy[-2:]) + 1900,
        month=int(ddmmyy[2:4]),
        day=int(ddmmyy[:2]),
    )
    d = datetime.date(2000, 1, 1)
    
    return (d - pydate).days // 365


# Gender is extracted from last number in CPR
def get_gender_from_cpr(cpr):
    # Calculates even number to determine if female
    gender = int(cpr[-1]) % 2 == 0
    
    return "Female" if gender else "Male"


# Find parents for each child
def parents_for_children(people):
    parents_for_child = {}
    for row in people:
        # Checks for children CPR in dict of people
        if 'Children' in row:
            # Splits row if multiple children 
            child_cprs = row['Children'].split()
            for cpr in child_cprs:
                if cpr not in parents_for_child:
                    parents_for_child[cpr] = []

                parents_for_child[cpr].append(row['CPR'])
   
    return parents_for_child


# Calculates each age difference to take the average
def average_age_difference_between_parents(people):
    parents_for_child = parents_for_children(people)
    # Calculate difference between parents
    parent_differences = []
    seen_parents = set()
    for child, parents in parents_for_child.items():
        assert len(parents) == 2
        parent_key = (parents[0], parents[1])
        # Ensure we aren't calculting difference twice
        if parent_key in seen_parents:
            continue

        parent_0_age = get_age_from_cpr(parents[0])
        parent_1_age = get_age_from_cpr(parents[1])
        parent_differences.append(abs(parent_0_age - parent_1_age))
        seen_parents.add(parent_key)

    print("{:.2f}".format(average(parent_differences)))


def average(list_of_numbers):
    return sum(list_of_numbers) / len(list_of_numbers)


# Finding grandparents by cross referencing their childrens children
def grandparents_for_children(people):
    # Reuse already found parents
    parents_for_child = parents_for_children(people)
    grandparents_for_child = {}
    for child, parents in parents_for_child.items():
        for parent in parents:
            if parent in parents_for_child:
                if child not in grandparents_for_child:
                    grandparents_for_child[child] = []
                #adding the parent's parents    
                grandparents_for_child[child].extend(parents_for_child[parent])

    return grandparents_for_child


# All grandparents in data set are alive, all children without grandparents listed will be considered to have dead grandparents
def num_alive_grandparents(people):
    # Get the number of children with grandparents and divide it by the total number of children
    grandparents_for_child = grandparents_for_children(people)
    parents_for_child = parents_for_children(people)
    ratio = (len(grandparents_for_child) / len(parents_for_child)) * 100
    
    print("{:.2f}%".format(ratio))


# Defines the sibling pairs
def num_siblings_for_child(people):
    parents_for_child = parents_for_children(people)
    child_for_parents = {}
    # Switching the keys and values to be {parent: [children]}
    for child, parents in parents_for_child.items():
        for parent in parents:
            if parent not in child_for_parents:
                child_for_parents[parent] = []
            child_for_parents[parent].append(child)

    num_siblings_for_child = {}
    for parent, children in child_for_parents.items():
        for child in children:
            # Number of siblings that individual has (subtract 1 so it doesn't include themselves)
            num_siblings_for_child[child] = len(children) - 1
    
    return num_siblings_for_child


def average_number_of_cousins(people):
    # Given as {child: [grandparents]}
    grandparents_for_child = grandparents_for_children(people)
    child_for_grandparents = {}
    # Switching the keys and values to be {grandparent: [children]}
    for child, grandparents in grandparents_for_child.items():
        for grandparent in grandparents:
            if grandparent not in child_for_grandparents:
                child_for_grandparents[grandparent] = []
            child_for_grandparents[grandparent].append(child)
    
    number_siblings = num_siblings_for_child(people)

    num_cousins = []
    # Cousins share grandparents but NOT parents (subtract out siblings)
    for grandparent, children in child_for_grandparents.items():
        for child in children:
            # Must subtract by one so the person you are counting for doesn't include themselves
            num_cousins_for_child = len(children) - number_siblings[child] - 1
            num_cousins.append(num_cousins_for_child)
    
    print("{:.2f}".format(average(num_cousins)))


# Based on previous calculations in dict of parents age of first child
def print_first_child_age_stats(people, gender, parent_gender):
    # From the people dict, extract the value "Parent age" defined above
    parent_ages = [int(x["Parent age"]) for x in people if x["Gender"] == gender and "Parent age" in x]
    columns = 'Age of first time' + ' ' + parent_gender
    print_distribution_of_values(columns, parent_ages)
    print('Maximum age of first-time', parent_gender, ': ', max(parent_ages))
    print('Minimum age of first-time', parent_gender, ': ', min(parent_ages))
    print('Average age of first-time', parent_gender, ': ', '{:.2f}'.format(average(parent_ages)))


# Finding children's parents and pairing them
def partners_for_person(people):
    parents_for_child = parents_for_children(people)
    partners_for_parent = {}
    # Finding childrens CPR, split if more than one
    for row in people:
        if 'Children' in row:
            baby_momma_or_daddy = []
            child_cprs = row['Children'].split()
            # Adding parents to all children
            for cpr in child_cprs:
                child_parents = parents_for_child[cpr]
                for child_parent_cpr in child_parents:
                    if child_parent_cpr != row["CPR"]:
                        baby_momma_or_daddy.append(child_parent_cpr)
            partners_for_parent[row["CPR"]] = list(set(baby_momma_or_daddy))
    
    return partners_for_parent


# Asking if there are any parents with multiple partners 
def num_multiple_partners(people):
    partners_for_parent = partners_for_person(people)

    total_multiple_partners = 0
    for partners in partners_for_parent.values():
        # More than one means multiple partners
        total_multiple_partners += int((len(partners) > 1))

    print("{:.1f}%".format(total_multiple_partners))


def category_for_height(height):
    height = int(height)
    if height < 165:
        return "short"
    elif height < 185:
        return "normal"
    else:
        return "tall"


# Defining the rows of CPR from people dict for later use 
def get_row_by_cpr(people):
    row_for_cpr = {}
    for row in people:
        row_for_cpr[row["CPR"]] = row

    return row_for_cpr


# Creating a tuple of partners by CPR
def get_couple_pairs(people):
    partners_for_parent = partners_for_person(people)
    partner_pairs = set()
    for person_cpr, partners in partners_for_parent.items():
        for x in partners:
            partner_pairs.add(tuple([person_cpr, x]))

    return partner_pairs


def height_of_couples(people):
    partner_pairs = get_couple_pairs(people)
    # Lambda allows us to sort according to the established categories for height
    percentage_of_pairs(people, partner_pairs, lambda x: category_for_height(x['Height']))


# Formats the values to percentages
def to_percentage_str(x):
    return str(round(x * 100, 2)) + "%"


# Print function for formatting of proper output
def print_distribution_of_values(category, values):
    total = len(values)
    counts = {}
    for x in values:
        if x not in counts:
            counts[x] = 0

        counts[x] += 1

    histogram = {k: to_percentage_str(v / total) for k, v in counts.items()}
    columns = [category, 'Percentage'] 
    print_table(histogram, columns)


# Function used for pairing of categories in percentage
def percentage_of_pairs(people, cpr_pairs, row_to_cat_funct):
    row_for_cpr = get_row_by_cpr(people)
    #l is left tuple value, r is right tuple value
    cat_for_partner_pair = [(row_to_cat_funct(row_for_cpr[l]), row_to_cat_funct(row_for_cpr[r])) for l, r in cpr_pairs]
    # In the category count we use sorted to keep the output consistent
    cat_count = {}
    for cat_pair in cat_for_partner_pair:
        cat_key = tuple(sorted(list(cat_pair)))

        if cat_key not in cat_count:
            cat_count[cat_key] = 0

        cat_count[cat_key] += 1

    total = sum(list(cat_count.values()))
    cat_percentage = {'/'.join(list(k)): to_percentage_str(v / total) for k, v in cat_count.items()}
    header = ["Groups", "Percentage"]
    print_table(cat_percentage, header)


# Percentage of tall children based on parent pairings
def height_of_children_parents(people):
    parent_to_child_pairs = get_parent_to_child_pairs(people)
    percentage_of_pairs(people, parent_to_child_pairs, lambda x: category_for_height(x['Height']))


# The BMI formula is kilograms / meter^2
def get_bmi(weight, height):
    # Converting height in cm to m
    height_meters = height / 100
    
    return weight / (height_meters * height_meters)


# Extract weight and height from table
def bmi_from_row(row):
    
    return get_bmi(int(row["Weight"]), int(row["Height"]))


# Catergories of BMI are taken from the official BMI standard 
def category_for_bmi(bmi):
    if bmi < 18.5:
        return "slim"
    elif bmi < 25:
        return "normal"
    else:
        return "fat"


# Comparing partners in relation to their BMI 
def bmi_of_couples(people):
    partner_pairs = get_couple_pairs(people)
    percentage_of_pairs(people, partner_pairs, lambda x: category_for_bmi(bmi_from_row(x)))


# Defining the Rhesus system in relation to blood inheritance
def is_possible_blood_sign_combo(parent1, parent2, child):
    # Parent1, parent2, child
    possible_sign_combos = {
        ('+', '+', '+'),
        ('+', '+', '-'),
        ('+', '-', '+'),
        ('+', '-', '-'),
        ('-', '-', '-'),
    }

    parent1_sign, parent2_sign, child_sign = parent1[-1], parent2[-1], child[-1]
    potential_sign_combo_1 = (parent1_sign, parent2_sign, child_sign) in possible_sign_combos
    potential_sign_combo_2 = (parent2_sign, parent1_sign, child_sign) in possible_sign_combos
    return potential_sign_combo_1 or potential_sign_combo_2


# Defining the ABO blood inheritance system
def is_possible_blood_symbol_combo(parent1, parent2, child):
    possible_combos = {
        # Parent1, parent2, child
        ("A", "A", "A"),
        ("A", "A", "O"),

        ("A", "B", "A"),
        ("A", "B", "B"),
        ("A", "B", "AB"),
        ("A", "B", "O"),

        ("A", "AB", "A"),
        ("A", "AB", "B"),
        ("A", "AB", "AB"),

        ("A", "O", "A"),
        ("A", "O", "O"),

        ("B", "B", "B"),
        ("B", "B", "O"),

        ("B", "AB", "A"),
        ("B", "AB", "B"),
        ("B", "AB", "AB"),

        ("B", "O", "B"),
        ("B", "O", "O"),

        ("AB", "AB", "A"),
        ("AB", "AB", "B"),
        ("AB", "AB", "AB"),

        ("AB", "O", "A"),
        ("AB", "O", "B"),
        ("O", "O", "O"),
    }
    
    parent1, parent2, child = parent1[:-1], parent2[:-1], child[:-1]
    # Checking both p1/p2 and p2/p1 combos for inheritance
    potential_combo_1 = (parent1, parent2, child) in possible_combos
    potential_combo_2 = (parent2, parent1, child) in possible_combos
    
    return potential_combo_1 or potential_combo_2


def name_for_row(row):
    return row["First name"] + ' ' + row["Last name"]


# Checking for potential non-biological parents by examining blood inheritance
def children_that_have_fake_parents(people):
    parents_for_child = parents_for_children(people)
    row_for_cpr = get_row_by_cpr(people)

    fake_children = []
    for cpr, parents in parents_for_child.items():
        row = row_for_cpr[cpr]
        # Getting blood types from both children and parents
        child_blood_type = row["Blood type"]
        parents_blood_type = [row_for_cpr[x]["Blood type"] for x in parents]
        # Checking if Rhesus inheritance is possible
        is_possible_blood_sign = is_possible_blood_sign_combo(
            parents_blood_type[0],
            parents_blood_type[1],
            child_blood_type
        )
        # Checking if ABO type inheritance is possible
        is_possible_blood_symbol = is_possible_blood_symbol_combo(
            parents_blood_type[0],
            parents_blood_type[1],
            child_blood_type
        )

        if is_possible_blood_sign and is_possible_blood_symbol:
            continue
        if not is_possible_blood_symbol and not is_possible_blood_sign:
            reason = "Not possible blood sign combination and not possible blood symbol combination"
        elif not is_possible_blood_sign:
            reason = "Not possible blood sign combination"
        elif not is_possible_blood_symbol:
            reason = "Not possible blood symbol combination"

        fake_children.append((row, reason))

    # Printing the table of children with non-biological parents
    print('Number of children total with at least one non-biological parent: ', len(fake_children), '/', len(people))
    fake_children_names = {name_for_row(x[0]): x[1] for x in fake_children}
    header = ["Name of child", "Reason for at least one non-biological parent"]
    print_table(fake_children_names, header, length=120)


# A donor / recipient table
def can_donate_to_blood_type(donor, recipient):
    # Donor: [recipient]
    donation_mapping = {
        'A+': ['A+', 'AB+'],
        'A-': ['A-', 'A+', 'AB-', 'AB+'],
        'B+': ['B+', 'AB+'],
        'B-': ['B-', 'B+', 'AB-', 'AB+'],
        'O+': ['A+', 'B+', 'AB+'],
        'AB+': ['AB+'],
        'AB-': ['AB-', 'AB+']
    }
    
    # O- is the universal donor meaning that it can donate to all other bloodtypes
    return donor == 'O-' or recipient in donation_mapping[donor]


# Finding all possible donor/recipient pairs by name for later use 
def pairs_that_can_donate_and_receive(people_pairs, people):
    row_for_cpr = get_row_by_cpr(people)
    pairs_that_can_donate = [
        (name_for_row(row_for_cpr[donor]), name_for_row(row_for_cpr[recipient]), row_for_cpr[donor]["Blood type"], row_for_cpr[recipient]["Blood type"])
        for donor, recipient in people_pairs
        if can_donate_to_blood_type(row_for_cpr[donor]["Blood type"], row_for_cpr[recipient]["Blood type"])
    ]
    header = ['Donor', 'Recipient', "Donor's blood type", "Recipient's blood type"]
    print_blood(pairs_that_can_donate, header)


# For use in donor/recepient relation between father/son
def get_parent_to_child_pairs(people):
    parent_to_child_pairs = []
    for row in people:
        if 'Children' in row:
            child_cprs = row['Children'].split()
            for cpr in child_cprs:
                parent_to_child_pairs.append((row['CPR'], cpr))

    return parent_to_child_pairs


# Finding which sons can receive blood from their father 
def fathers_that_can_donate_to_sons(people):
    males = [x for x in people if x["Gender"] == "Male"]
    fathers_to_child_pairs = get_parent_to_child_pairs(males)
    fathers_to_son_pairs = [
        (father, child) for father, child in fathers_to_child_pairs if get_row_by_cpr(people)[child]["Gender"] == 'Male'
    ]
    pairs_that_can_donate_and_receive(fathers_to_son_pairs, people)


# Finding which children can donate to their grandparents
def child_that_can_donate_to_grandparents(people):
    grandparents_for_child = grandparents_for_children(people)

    child_grandparent_pairs = []
    for child, grandparents in grandparents_for_child.items():
        for grandparent in grandparents:
            child_grandparent_pairs.append((child, grandparent))

    pairs_that_can_donate_and_receive(child_grandparent_pairs, people)


# Formatting used for printing tables nicely
def print_table(dict_of_values, columns, length=45):
    print()
    print("{:<30} {:<30}".format(columns[0], columns[1]))
    print('-' * length)
    print("\n".join("{:<30} {:<30}".format(k, v) for k, v in sorted(dict_of_values.items())))
    print()


# Formatting for donor related tables 
def print_blood(list_of_lists, columns):
    # Print columns
    for column_name in columns:
        print("{:<30}".format(column_name), end='')
    print()
    print('-' * 120)
    for x in list_of_lists:
        print("{:30} {:30} {:30} {:30}".format(x[0], x[1], x[2], x[3]))
    print()


# Main program
def main():
    people = read_people_as_dict('people.db')
    
    #To preserve space we only print first 10 entries in the people.db file 
    print_people_as_table(people[:10])

    # Is the age and gender distribution "normal" in the database? A yes/no answer is not good enough.
    print_distribution_of_values('Age', [bucket_age(x["Age"]) for x in people])
    print_distribution_of_values('Gender', [x["Gender"] for x in people])

    # At what age do the men become fathers first time (max age, min age, average age)?
    # Is the distribution of first-time fatherhood age "normal"? A yes/no answer is not good enough.
    print_first_child_age_stats(people, gender="Male", parent_gender = "fathers")

    # At what age does the women become mothers first time (max age, min age, average age)?
    # Is the distribution of first-time motherhood age "normal"? A yes/no answer is not good enough.
    print_first_child_age_stats(people, gender="Female", parent_gender = "mothers")

    # How many men and women do not have children (in percent)?
    male_rows = [x for x in people if x["Gender"] == "Male"]
    female_rows = [x for x in people if x["Gender"] == "Female"]
    male_rows_without_children = [x for x in male_rows if "Children" not in x]
    female_rows_without_children = [x for x in female_rows if "Children" not in x]
    format_men_len = "{:.2f}%".format((len(male_rows_without_children) / len(male_rows) * 100))
    print()
    print('Percentage of men without children : ', format_men_len)
    format_women_len =  "{:.2f}%".format((len(female_rows_without_children) / len(female_rows) * 100))
    print('Percentage of women without children : ', format_women_len)

    # Is the firstborn likely to be male or female?
    print_distribution_of_values('Gender of firstborn', [x["First child gender"] for x in people if "First child gender" in x])

    # What is the average age difference between the parents (with a child in common obviously)?
    print('Average age difference between parents:')
    average_age_difference_between_parents(people)

    # How many people in percent has at least one grandparent that is still alive? A person is living if he/she is in the database.
    print()
    print('Percentage of people who have at least one grandparent still alive:')
    num_alive_grandparents(people)


    # For those who have cousins, what is the average number of cousins?
    print()
    print('Average number of cousins per individual (if they have cousins):')
    average_number_of_cousins(people)

    # How many men/women (percentage) have children with more than one woman/man?
    print()
    print('Percentage of men/women who have children with more than one woman/man:')
    num_multiple_partners(people)

    # Do tall people marry (or at least get children together)? To answer that, calculate
    # the percentages of tall/tall, tall/normal, tall/short, normal/normal, normal/short,
    # and short/short couples. Decide your own limits for tall, normal and short, and if
    # they are the same for men and women.
    print()
    print('The percentages of couples in respect to height difference:')
    height_of_couples(people)

    # Do tall parents get tall children?
    print('Percentage of couples who get tall children: ')
    height_of_children_parents(people)

    # Do fat people marry (or at least get children together)? To answer that,
    # calculate the percentages of fat/fat, fat/normal, fat/slim, normal/normal,
    # normal/slim, and slim/slim couples. Decide your own limits for fat, normal and
    # slim. Calculate the BMI, and let that be the fatness indicator.
    print('The percentages of couples in respect to BMI difference:')
    bmi_of_couples(people)

    # Using the knowledge of blood group type inheritance, are there any children in
    # the database where you can safely say that at least one of the parents are not
    # the real parent. If such children exists, make a list of them. In the report you
    # must discuss how you determine that the parent(s) of the child are not the "true"
    # parents.
    children_that_have_fake_parents(people)

    # Make a list of fathers who can donate blood to their sons. The list must identify
    # must the father and the son(s) and their blood type. You must write the length of
    # the list in the report.
    print('Fathers that can donate blood to their sons: ')
    fathers_that_can_donate_to_sons(people)

    # Make a list of persons who can donate blood to their grandparents. The list must
    # identify must the person, the grandparent(s) and their blood type. You must write
    # the length of the list in the report.
    print('People that can donate blood to their grandparent: ')
    child_that_can_donate_to_grandparents(people)

# This allows us to comment out and run functions as we please
if __name__ == "__main__":
    main()
