import os
import re
import copy
from enum import Enum

# Match: I. A. 1. a. (1) (a) and any variations of those. Uses groups, which are later combined to get the value of the
# pattern found
roman_numeral_regex = r"(\(?(?:\d|(a-z)){1})?(\w?[IVX]*)(\)|\.)"
zero_order = [0, 0, 0, 0, 0, 0]
base_order = [1, 0, 0, 0, 0, 0]

# Apply these headers (###) to these positions. 0 is the outermost I. II. III. position, and 1 is the A. B. C. position.
position_to_header_mapping = {
    0: "###",
    1: "####"
}


class Action(Enum):
    """
    Possible actions that can be taken on an order.
    """
    RESET = "reset"  # go back to base order  [2, 1, 3, 1, 0, 0] => [1, 0, 0, 0, 0, 0]
    CONTINUE = "continue"  # increment the current order's count [2, 1, 3, 1, 0, 0] => [2, 1, 3, 2, 0, 0]
    DOWN = "down"  # go down a level and start counting there [2, 1, 3, 1, 0, 0] => [2, 1, 3, 1, 1, 0]
    UP = "up"  # go up one level and increment that level [2, 1, 3, 1, 0, 0] => [2, 1, 4, 0, 0, 0]
    UP2 = "up_2"  # go up two levels and increment that level [2, 1, 3, 1, 0, 0] => [2, 2, 0, 0, 0, 0]
    UP3 = "up_3"  # go up three levels and increment that level [2, 1, 3, 1, 0, 0] => [3, 0, 0, 0, 0, 0]
    # why not more? need to think about the repercussions of this... TODO


def cls():
    """
    Clear the console
    :return: None
    """
    os.system('cls' if os.name == 'nt' else 'clear')


def change_order(action, order):
    """
    Convert from one order to another based on the given argument
    """
    pos = next((index - 1 for index, val in enumerate(order) if val == 0), len(order) - 1)
    if action == Action.CONTINUE:
        # Increase the current position by 1, e.g. going from I. to II., or from A. to B.
        order[pos] += 1
    elif action == Action.RESET:
        order = copy.deepcopy(base_order)
    elif action == Action.DOWN:
        # Go down one level, e.g. from I. to A. or from A. to 1.
        order[pos + 1] = 1
    elif action == Action.UP:
        # Go up one level, e.g. from A. to I. or from 1. to A.
        if pos == 0:
            order[0] = 1  # Reset the first position to 1
        else:
            order[pos] = 0
            order[pos - 1] += 1
    elif action == Action.UP2:
        # Go up two levels, e.g. from 1. to I. or from a. to A.
        if pos in [0, 1]:
            order[0] = 1
            order[1] = 0
        else:
            order[pos] = 0
            order[pos - 1] = 0
            order[pos - 2] += 1
    elif action == Action.UP3:
        # Go up three levels, e.g. from a. to I.
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


def get_outline_formatted_strings(order, full_repr=True) -> (str, str):
    """
    Given an order, print what it should look like in the final output
    :param order: list, something like [1, 2, 1, 0, 0, 0]
    :param full_repr: bool, whether to include . and () in both the outline_formatted_numeral and the last_added_order.
        That is, A. and (1) vs. A and 1
    :return:
        outline_formatted_numeral (e.g. ### [1A], which would be ### [1A.] if full_repr is True),
        last_added_order (e.g. A, which would be A. if full_repr is True)
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


def get_order_of_outline_formatted_numeral(outline_formatted_numeral):
    """
    Convert something like 1A1b3 to [1, 1, 1, 2, 3, 0]
    :param outline_formatted_numeral: str, something like 1A1b3
    :return: list[int], the order
    """
    outline_formatted_numeral = str(outline_formatted_numeral)
    result = copy.deepcopy(base_order)
    if outline_formatted_numeral != "":
        result[0] = int(outline_formatted_numeral[0])
    if len(outline_formatted_numeral) > 1:
        try:
            int(outline_formatted_numeral[1])
            result[0] = int(outline_formatted_numeral)
        except Exception:
            result[1] = ord(outline_formatted_numeral[1].upper()) - 64
    if len(outline_formatted_numeral) > 2:
        result[2] = int(outline_formatted_numeral[2])
    if len(outline_formatted_numeral) > 3:
        result[3] = ord(outline_formatted_numeral[3]) - 96
    if len(outline_formatted_numeral) > 4:
        result[4] = int(outline_formatted_numeral[4])
    if len(outline_formatted_numeral) > 5:
        result[5] = ord(outline_formatted_numeral[5]) - 96
    return result


def next_possibility(action, order):
    """
    Return the new order after performing said action.
    :param action: Action
    :param order: list[int]
    :return: list[int], str: the new order, and the last added order (e.g. A., 1., (1), (a))
    """
    new_order = order.copy()
    new_order = change_order(action, new_order)
    printed_order, last_added_order = get_outline_formatted_strings(new_order, full_repr=True)
    return new_order, last_added_order


def next_order(i, order, replacements, match_objects, text):
    """
    With all match_objects in the text (matching all romans found), as well as a current order (from the previous match
    object's order) identify what order the match at index i should be.
    :param i: int, index within match_object
    :param order: list[int] the order of the previous match_object
    :param replacements: list[str] the replacements up to the last match_object, what the match (roman) should be replaced with
    :param match_objects: list[re.Match] all roman point matches in the text (Match objects in python's re default library)
    :param text: str, The text for which we found all the matches. a slightly cleaned version of the original outline.
    :return:
    """
    match_object = match_objects[i]
    match, match_start, match_end = match_object.group(1), match_object.start(1), match_object.end(1)
    previous_previous_item = replacements[i - 2].replace('\n', '').replace('\t', '') if i > 1 else None
    previous_item = replacements[i - 1].replace('\n', '').replace('\t', '') if i > 0 else None
    next_match_object = match_objects[i + 1] if i < len(match_objects) - 1 else None
    next_match = match_object.group(1) if next_match_object else None

    # try all the possibilities of going up or down in roman numeral order, and see which one matches the current match
    current_possibilities = [next_possibility(action, order) for action in
                             [Action.CONTINUE, Action.DOWN, Action.UP, Action.UP2, Action.UP3]]

    for idx in [0, 1, 2, 3]:
        if current_possibilities[idx][1] == match:
            return current_possibilities[idx][0]
    if is_roman(match):
        return get_order_of_outline_formatted_numeral(roman_to_number(match))

    # didn't find an order, going to ask the user about it.
    cls()
    # print the previous two matches
    previous_match_start_index = 0
    if i > 1:
        previous_previous_match_start_index = match_objects[i - 2].start(1)
        previous_match_start_index = match_objects[i - 1].start(1)
        previous_previous_whole_item = text[previous_previous_match_start_index:previous_match_start_index]
        previous_previous_whole_item = previous_previous_whole_item.replace("\n", "")
        print(previous_previous_whole_item)
    if i > 0:
        previous_whole_item = text[previous_match_start_index:match_start]
        previous_whole_item = previous_whole_item.replace("\n", "")
        print(previous_whole_item)
    if i < len(match_objects) - 1:
        next_item_start_index = match_objects[i + 1].start(1)
    else:
        next_item_start_index = len(text)
    current_whole_item = text[match_start:next_item_start_index].replace("\n", "")
    print(f"Found an item that doesn't match the ordering: {current_whole_item}")
    return get_order_advancement_from_user(order, f"(match to set: {next_match})")


def get_order_advancement_from_user(previous_order, more_information=""):
    user_input_valid = False
    while not user_input_valid:
        print(
            f"Previous order: {previous_order} ({get_outline_formatted_strings(previous_order, False)[0]}) {more_information}.")
        continue_order = next_possibility(Action.CONTINUE, previous_order)[0]
        down_order = next_possibility(Action.DOWN, previous_order)[0]
        up_order = next_possibility(Action.UP, previous_order)[0]
        up2_order = next_possibility(Action.UP2, previous_order)[0]
        up3_order = next_possibility(Action.UP3, previous_order)[0]
        print("Type nothing to skip this item.")
        print(
            f"Type [c]ontinue to advance the ordering: {continue_order} ({get_outline_formatted_strings(continue_order, False)[0]})")
        print(f"Type [d]own to go down a level: {down_order} ({get_outline_formatted_strings(down_order, False)[0]})")
        print(f"Type [u]p to go back up a level: {up_order} ({get_outline_formatted_strings(up_order, False)[0]})")
        print(
            f"Type [up2] to go back up two levels: {up2_order} ({get_outline_formatted_strings(up2_order, False)[0]})")
        print(
            f"Type [up3] to go back up three levels: {up3_order} ({get_outline_formatted_strings(up3_order, False)[0]})")
        user_input = input("> ")
        if user_input == "":
            return previous_order  # handle this case specially
        elif user_input == "c":
            return continue_order
        elif user_input == "d":
            return down_order
        elif user_input == "u":
            return up_order
        elif user_input == "u2":
            return up2_order
        elif user_input == "u3":
            return up3_order


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
    order = copy.deepcopy(zero_order)
    replacements = []
    match_objects = list(re.finditer(f"\n({roman_numeral_regex}) ", text))
    pos = None
    for i, match_object in enumerate(match_objects):
        old_order = copy.deepcopy(order)  # for handling if the order does not change in this iteration
        match, match_start, match_end = match_object.group(1), match_object.start(1), match_object.end(1)
        if i == 0:
            # special handling for starting in the middle of an outline
            print("Interpreting the first match as a roman numeral...")
            try:
                order[0] = roman_to_number(match)
                print("Interpreted as position:", order[0])
            except:
                print(f"Failed to interpret the first match, which is: {match}")
                print("Type nothing to skip this match, otherwise type the integer value of this roman numeral.")
                user_input = input("> ")
                if user_input:
                    order = get_order_of_outline_formatted_numeral(user_input)
        if i != 0:
            order = next_order(i, order, replacements, match_objects, text)

        if order == old_order:
            replacement_value = match_object.group(0)
        else:
            replacement_value, _ = get_outline_formatted_strings(order, full_repr=False)

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
    collected_text = []
    leftover_text = text
    for new_value in replacements:
        # Do NOT use the following: text = re.sub(rf"\n{roman_numeral_regex} ", new_value, text, count=1)
        # this is because we may try to replace with a value that is the same, so the regex will find the value again
        match_object = re.search(rf"\n{roman_numeral_regex} ", leftover_text)
        collected_text.append(leftover_text[:match_object.start(0)])
        collected_text.append(new_value)
        leftover_text = leftover_text[match_object.end(0):]
    collected_text.append(leftover_text)
    return "".join(collected_text)


# Get the outline
with open("outline.txt", "r") as f:
    text = "\n" + f.read()

text = re.sub(rf"(?<!-)\n(?!{roman_numeral_regex}|\n)", " ", text)
text = re.sub(rf"\n(?!{roman_numeral_regex}|\n)", "", text)
while "\n\n" in text:
    text = re.sub(r"\n\n", "\n", text)
text = text.replace("\t", "")

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

# bold points
new_text = re.sub("- \[", "- **[", new_text)


def replace_hashtags(match):
    hashtags = match.group(1)  # Capture the matched hashtags
    return "- {} **[".format(hashtags)  # Construct the replacement string


new_text = re.sub("- (#+) \[", replace_hashtags, new_text)
new_text = re.sub("\]\\n", "]** ", new_text)
print(new_text)

with open("updated_outline.txt", "w") as f:
    f.write(new_text)
