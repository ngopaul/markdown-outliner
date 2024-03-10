import re
import copy

roman_numeral_regex = r"(\(?(?:\d|(a-z)){1})?(\w?[IVX]*)(\)|\.) "  # Matches: I. A. 1. a. (1) (a) and any variations of those
base_order = [1, 0, 0, 0, 0, 0]

# Apply these headers (###) to these positions. 0 is the outermost I. II. III. position, and 1 is the A. B. C. position.
position_to_header_mapping = {
    0: "###",
    1: "####"
}

def change_order(arg, order):
    """
    Convert from one order to another based on the given argument
    """
    pos = next((index - 1 for index, val in enumerate(order) if val == 0), len(order) - 1)
    if arg == "continue":
        # Increase the current position by 1, i.e. going from I. to II., or from A. to B.
        order[pos] += 1
    elif arg == "reset":
        order = copy.deepcopy(base_order)
    elif arg == "down":
        # Go down one level, i.e. from I. to A. or from A. to 1.
        order[pos + 1] = 1
    elif arg == "up":
        # Go up one level, i.e. from A. to I. or from 1. to A.
        if pos == 0:
            order[0] = 1  # Reset the first position to 1
        else:
            order[pos] = 0
            order[pos - 1] += 1
    elif arg == "up_2":
        # Go up two levels, i.e. from 1. to I. or from a. to A.
        if pos in [0, 1]:
            order[0] = 1
            order[1] = 0
        else:
            order[pos] = 0
            order[pos - 1] = 0
            order[pos - 2] += 1
    elif arg == "up_3":
        # Go up three levels, i.e. from a. to I.
        if pos in [0, 1, 2]:
            order[0] = 1
            order[1] = 0
            order[2] = 0
        else:
            order[pos] = 0
            order[pos - 1] = 0
            order[pos - 2] = 0
            order[pos - 3] += 1
    return order


def print_order(order, full_repr=True):
    """
    Given an order, print what it should look like in the final output
    :param order: list, something like [1, 2, 1, 0, 0, 0]
    :param full_repr: bool, whether to include . and (). That is, A. (1) vs. A 1
    :return:
    """
    # Get the highest non-zero index
    pos = next((index - 1 for index, val in enumerate(order) if val == 0), len(order) - 1)
    result = f"{str(order[0])}"  # immediately add the digit value of the roman to the beginning, since it is guaranteed
    # to be there
    last_added_order = result
    prefix = ""

    # special handling for high level positions, become headers
    if pos in position_to_header_mapping:
        prefix = position_to_header_mapping[pos] + " "

    wrap_start = ("(" if full_repr else "")
    wrap_end = (")" if full_repr else "")
    suffix = ("." if full_repr else "")

    if pos > 0:
        last_added_order = chr(order[1] % 26 + 64) + suffix  # Uppercase letters: A. B.
        result += last_added_order
    if pos > 1:
        last_added_order = str(order[2]) + suffix  # 1. 2.
        result += last_added_order
    if pos > 2:
        last_added_order = chr(order[3] % 26 + 96) + suffix  # Lowercase letters: a. b.
        result += last_added_order
    if pos > 3:
        last_added_order = f"{wrap_start}{order[4]}{wrap_end}"  # (1) (2)
        result += last_added_order
    if pos > 4:
        last_added_order = f"{wrap_start}{chr(order[3] % 26 + 96)}{wrap_end}"  # (a) (b)
        result += last_added_order
    return f"{prefix}[{result}]", last_added_order


def set_order(arg):
    arg = str(arg)
    result = copy.deepcopy(base_order)
    if arg != "":
        result[0] = int(arg[0])
    if len(arg) > 1:
        try:
            int(arg[1])
            result[0] = int(arg)
        except Exception:
            result[1] = ord(arg[1].upper()) - 64
    if len(arg) > 2:
        result[2] = int(arg[2])
    if len(arg) > 3:
        result[3] = ord(arg[3]) - 96
    if len(arg) > 4:
        result[4] = int(arg[4])
    return result


def next_possibility(arg, order):
    new_order = order.copy()
    new_order = change_order(arg, new_order)
    printed_order, last_added_order = print_order(new_order, full_repr=True)
    return new_order, last_added_order


def next_order(i, order, replacements, matches):
    match = matches[i]
    previous_previous_item = replacements[i - 2].replace('\n', '').replace('\t', '') if i > 1 else None
    previous_item = replacements[i - 1].replace('\n', '').replace('\t', '') if i > 0 else None
    next_match = matches[i + 1] if i < len(matches) - 1 else None

    # try all the possibilities of going up or down in roman numeral order, and see which one matches the current match
    current_possibilities = [next_possibility(arg, order) for arg in ["continue", "down", "up", "up_2", "up_3"]]

    for i in [0, 1, 2, 3]:
        if current_possibilities[i][1] == match:
            return current_possibilities[i][0]
    if is_roman(match):
        return set_order(roman_to_number(match))
    user_input = input(f"Previous matches: '{previous_previous_item}', '{previous_item}'\nCurrent order: {order}\n Found match: {match}, next match: {next_match}. Enter replacement value: ")
    return set_order(user_input)


def is_roman(roman):
    return 'I' in roman or 'V' in roman or 'X' in roman


def roman_to_number(roman):
    # remove any non-roman characters
    roman = roman.replace(".", "")
    roman_numerals = {'I': 1, 'V': 5, 'X': 10}
    number = 0
    prev_value = 0
    for symbol in reversed(roman):
        value = roman_numerals[symbol]
        if value >= prev_value:
            number += value
        else:
            number -= value
        prev_value = value
    return number


def generate_replacement_list(text):
    order = copy.deepcopy(base_order)
    replacements = []
    matches = re.findall(f"\n{roman_numeral_regex}", text)
    # combine all the groups in matches
    matches = [''.join(match) for match in matches]
    pos = None
    for i in range(len(matches)):
        if i == 0:
            # special handling for starting in the middle of an outline
            print("Interpreting the first match as a roman numeral...")
            order[0] = roman_to_number(matches[i])
            print("Interpreted as position:", order[0])
        if i != 0:
            order = next_order(i, order, replacements, matches)
        replacement_value, _ = print_order(order, full_repr=False)

        next_pos = next((index - 1 for index, val in enumerate(order) if val == 0), len(order) - 1)

        indentation = "\t" * next_pos + "- "
        # indentation = "- " # ignore indentation
        replacement_value = indentation + replacement_value
        if pos is not None and pos > next_pos:
            replacement_value = "\t" + indentation + "\n" + replacement_value
        pos = next_pos

        replacements.append(f"\n\n{replacement_value}\n")
    return replacements


def replace_expressions(text, replacements):
    for new_value in replacements:
        text = re.sub(f"\n{roman_numeral_regex}", new_value, text, count=1)
    return text


# Get the outline
with open("outline.txt", "r") as f:
    text = "\n" + f.read()

text = re.sub(rf"(?<!-)\n(?!{roman_numeral_regex}|\n)", " ", text)
text = re.sub(rf"\n(?!{roman_numeral_regex}|\n)", "", text)
while "\n\n" in text:
    text = re.sub(r"\n\n", "\n", text)

print("Simplified Outline:")
print(text)
print()

replacements = generate_replacement_list(text)

new_text = replace_expressions(text, replacements)
while "- \n" in new_text:
    new_text = re.sub("\n\s+- \n", "\n", new_text)
while "\n\n" in new_text:
    new_text = re.sub(r"\n\n", "\n", new_text)
new_text = re.sub(r"\n\s+-\s+\n-", "\n-", new_text)
## bold points
new_text = re.sub("- \[", "- **[", new_text)

def replace_hashtags(match):
    hashtags = match.group(1)  # Capture the matched hashtags
    return "- {} **[".format(hashtags)  # Construct the replacement string

new_text = re.sub("- (#+) \[", replace_hashtags, new_text)
new_text = re.sub("\]\\n", "]** ", new_text)
print(new_text)

with open("updated_outline.txt", "w") as f:
    f.write(new_text)