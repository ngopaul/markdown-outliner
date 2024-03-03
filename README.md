# Outliner

Convert the text of an outline in Roman format (I. A. 1. a. 2.), 
as can be automatically done by an iphone or by an OCR application,
into something that is markdown- and logseq-friendly, for pasting
into another application.

Original code by Dinushka Herath; Modified by Paul Ngo to have no dependencies

## Usage

1. Paste the contents of the outline into `outline.txt`
2. Fix lines that start with A., 2., etc. that are not true points in the outline.
3. Run `python outlineize.py` in a terminal
   1. If it asks for replacements, generally this means that the 
   outlining process failed. Look at the nearby/surrounding detected
   outline points to find out where it is incorrect.

Now the re-formatted outline is in `updated_outline.txt`.

## Requirements

1. `python`. You will have to install xcode tools on macOS.

## Further Notes

- Requires that the outline be formatted like "I. ". That is, a new line, 
followed by the roman numeral or number, followed by a period, 
followed by a space, then the contents of the point. 
- It is okay for the point to have newlines in the middle of it.
- You can't start in the middle of an outline, like "C. " or something 
like that. You must start from "I. ". I get around this by just typing
"I. lorem ipsum" up to the point where it's the content I want to paste