import re

roman_numeral_regex = r"\w\d?[IVX]*\."

def change_order(arg, order):
    # Get the highest non-zero index
    pos = next((index - 1 for index, val in enumerate(order) if val == 0), len(order) - 1)
    if arg == "continue":
        order[pos] += 1
    elif arg == "reset":
        order = [1, 0, 0, 0, 0]
    elif arg == "up":
        if pos <= 3:
            order[pos + 1] = 1
    elif arg == "down":
        if pos == 0:
            order[0] = 1
        else:
            order[pos] = 0
            order[pos - 1] += 1
    elif arg == "down2":
        if pos in [0, 1]:
            order[0] = 1
            order[1] = 0
        else:
            order[pos] = 0
            order[pos - 1] = 0
            order[pos - 2] += 1
    return order


def print_order(order):
    # Get the highest non-zero index
    pos = next((index - 1 for index, val in enumerate(order) if val == 0), len(order) - 1)
    result = f"{str(order[0])}"
    last_added_order = result
    prefix = ""
    if pos == 0:
    	prefix = "### "
    if pos == 1:
    	prefix = "#### "
    if pos > 0:
        last_added_order = chr(order[1] % 24 + 64) # Uppercase letters
        result += last_added_order
    if pos > 1:
        last_added_order = str(order[2])
        result += last_added_order
    if pos > 2:
        last_added_order = chr(order[3] % 24 + 96)  # Lowercase letters
        result += last_added_order
    if pos > 3:
        last_added_order = str(order[4])
        result += last_added_order
    return f"{prefix}[{result}]", last_added_order


def set_order(arg):
    arg = str(arg)
    result = [1, 0, 0, 0, 0]
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
    printed_order, last_added_order = print_order(new_order)
    return new_order, last_added_order


def next_order(i, order, replacements, matches):
    match = matches[i]
    previous_previous_item = replacements[i - 2].replace('\n', '').replace('\t', '') if i > 0 else None
    previous_item = replacements[i - 1].replace('\n', '').replace('\t', '') if i > 1 else None
    next_match = matches[i + 1] if i < len(matches) - 1 else None

    current_possibilities = [next_possibility(arg, order) for arg in ["up", "continue", "down", "down2"]]

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
    order = [1, 0, 0, 0, 0]
    replacements = []
    matches = re.findall(r"\n(\w\d?[IVX]*)\.", text)
    pos = None
    for i in range(len(matches)):
        if i != 0:
            order = next_order(i, order, replacements, matches)
        replacement_value, _ = print_order(order)

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
        text = re.sub(rf"\n{roman_numeral_regex} ", new_value, text, count=1)
    return text


# Get the outline
with open("outline.txt", "r") as f:
    text = "\n" + f.read()

text = re.sub(rf"(?<!-)\n(?!{roman_numeral_regex}|\n)", " ", text)
text = re.sub(rf"\n(?!{roman_numeral_regex}|\n)", "", text)
while "\n\n" in text:
    text = re.sub(r"\n\n", "\n", text)

print("=====")
print(text)
print("=====", flush=True)

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