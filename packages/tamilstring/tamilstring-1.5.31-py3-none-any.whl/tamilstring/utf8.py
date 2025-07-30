import re

suffics = "ாிீுூெேைொோௌ"
vowel = "அஆஇஈஉஊஎஏஐஒஓஔ"
charector = "௦௧௨௩௪௫௬௭௮௯௰௱௲௳௴௵௶௷௹௺"
prefixs = "கஙசஞடணதநபமயரலவழளறனஶஜஷஸஹ"

PATTERN = "([{0}](?:[{1}்](?:[ஷர](?:[{1}்])?)?)?|[{2}{3}ஃ])".format(prefixs,suffics,vowel,charector)

def get_letters(string):
    return re.compile(PATTERN).findall(string)
 

def unmatch_indeces(string):
    index_position, matches, unmatches = 0,[],[]
    for match in re.finditer(PATTERN, string):
        start, end = match.start(), match.end()
        if index_position < start: 
            unmatches.append([index_position,start])
        matches.append(string[start:end])
        index_position = end
    if index_position < len(string): 
        unmatches.append([index_position,len(string)])
    return unmatches
 

def split_letter(letter):
    if is_composite(letter):
        for vowel_let, vowel_sym in zip(vowel[1:],suffics):
            if letter[-1] == vowel_sym:
                return (letter[:-1]+'்', vowel_let)
        else:
            return (letter+'்', "அ")
    else:
        return (None,None) 
    

def make_letter(letter1,letter2): 
    if is_vowel(letter1) and is_consonent(letter2):
        constant_ = letter2
        vowel_ = letter1
        for vowel_let, vowel_sym in zip(vowel[1:],suffics):
            if vowel_ == vowel_let:
                return constant_[:-1] + vowel_sym
        else:
            return constant_
    elif is_vowel(letter2) and is_consonent(letter1):
        constant_ = letter1
        vowel_ = letter2
        for vowel_let, vowel_sym in zip(vowel[1:],suffics):
            if vowel_ == vowel_let:
                return constant_[:-1] + vowel_sym
        else:
            return constant_[:-1] 
    else:
        return None


def is_vowel(unicodes):
    letter = verify(unicodes)
    if letter != False: 
        if letter in vowel:
            return True
        else:
            return False


def is_consonent(unicodes):
    letter = verify(unicodes)
    if letter != False: 
        if (letter[:-1] in prefixs or letter[:-1] == "க்ஷ") and letter[-1] == "்":
            return True
        else:
            return False


def is_composite(unicodes):
    letter = verify(unicodes)
    if letter != False:
        if (letter[:-1] in prefixs or letter[:-1] == "க்ஷ") and letter[-1] in suffics:
            return True
        elif letter in prefixs or letter == "க்ஷ":
            return True
        else:
            return False


def verify(unicodes):
    letter_list = get_letters(unicodes)
    if len(letter_list) != 1:
        return False
    else:
        return letter_list[0]
