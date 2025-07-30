# TamilString

[![PyPI Version](https://img.shields.io/pypi/v/tamilstring)](https://pypi.org/project/tamilstring/)
[![License](https://img.shields.io/pypi/l/tamilstring)](https://gitlab.com/boopalan-dev/tamilstring/-/blob/main/LICENSE)

**English:**

TamilString is a Python library designed to simplify the handling and manipulation of Tamil Unicode characters, enabling developers to process Tamil text more efficiently in their applications.

**தமிழ்:**

TamilString என்பது தமிழ் யூனிகோட் எழுத்துகளை எளிதாக கையாளவும், செயலாக்கவும் உதவும் ஒரு Python நூலகமாகும், இது டெவலப்பர்களுக்கு தங்கள் பயன்பாடுகளில் தமிழ் உரையை சிறப்பாக செயல்படுத்த உதவுகிறது.

## Table of Contents

1. [Inspiration - தூண்டுதல்](#inspiration---தூண்டுதல்)
2. [Features - அம்சங்கள்](#features---அம்சங்கள்)
3. [Installation - நிறுவல்](#installation---நிறுவல்)
4. [Usage - பயன்பாடு](#usage---பயன்பாடு)
5. [Contributing - பங்களிப்பு](#contributing---பங்களிப்பு)
6. [License - உரிமம்](#license---உரிமம்)
7. [Acknowledgments - நன்றியுரைகள்](#acknowledgments---நன்றியுரைகள்)
8. [Contributors - பங்களிப்பாளர்கள்](#contributors---பங்களிப்பாளர்கள்)

## Inspiration - தூண்டுதல்

**English:**

TamilString was inspired by the [Open-Tamil](https://pypi.org/project/Open-Tamil/) project, which offers a set of Python libraries for Tamil text processing. While Open-Tamil laid the groundwork, TamilString aims to enhance and expand these capabilities. For instance, TamilString addresses specific issues found in Open-Tamil, such as the inaccurate output when handling complex Tamil ligatures like 'ஸ்ரீ'. By improving the processing of such characters, TamilString provides more accurate and reliable results for developers working with Tamil text.

**தமிழ்:**

TamilString திட்டம் [Open-Tamil](https://pypi.org/project/Open-Tamil/) திட்டத்தால் தூண்டப்பட்டது, இது தமிழ் உரை செயலாக்கத்திற்கான Python நூலகங்களை வழங்குகிறது. Open-Tamil அடித்தளத்தை அமைத்தபோதிலும், TamilString இந்த திறன்களை மேம்படுத்த மற்றும் விரிவாக்க நோக்கத்துடன் உருவாக்கப்பட்டது. உதாரணமாக, Open-Tamil இல் காணப்படும் 'ஸ்ரீ' போன்ற சிக்கலான தமிழ் லிகேச்சர்களை கையாளும்போது ஏற்படும் தவறான வெளியீட்டை TamilString தீர்க்கிறது. இப்படியான எழுத்துகளைச் சரியாக செயலாக்குவதன் மூலம், தமிழ் உரையுடன் பணிபுரியும் டெவலப்பர்களுக்கு TamilString மேலும் துல்லியமான மற்றும் நம்பகமான முடிவுகளை வழங்குகிறது. 

## Features - அம்சங்கள்

**English:**

- Comprehensive support for Tamil Unicode character manipulation.
- Functions for transliteration between Tamil and other scripts.
- Tools for text normalization and validation specific to the Tamil language.

**தமிழ்:**

- தமிழ் யூனிகோட் எழுத்துகளை முழுமையாக கையாள்வதற்கான ஆதரவு.
- தமிழ் மற்றும் பிற எழுத்துக்களுக்கிடையே எழுத்துப்பெயர்ப்பு செய்யும் செயல்பாடுகள்.
- தமிழ் மொழிக்கேற்ப உரை சாதாரணமாக்கல் மற்றும் சரிபார்ப்பு கருவிகள்.

## Installation - நிறுவல்

**English:**

Install the latest version of TamilString using pip:

```bash
pip install tamilstring
```

**தமிழ்:**

pip பயன்படுத்தி TamilString இன் சமீபத்திய பதிப்பை நிறுவவும்:

```bash
pip install tamilstring
```

## Usage - பயன்பாடு

**English:**

Here's a basic example demonstrating how to use TamilString:

```python
import tamilstring

# Example function usage
string = 'தமிழ்'
tamil_str = tamilstring.String(string)

# Splitting the string into characters
characters = list(tamil_str)
print(characters)
```

**Output:**

```python
['த', 'மி', 'ழ்']
```

**தமிழ்:**

TamilString ஐ எவ்வாறு பயன்படுத்துவது என்பதை காட்டும் ஒரு அடிப்படை எடுத்துக்காட்டு:

```python
import tamilstring

# எடுத்துக்காட்டு செயல்பாடு பயன்பாடு
string = 'தமிழ்'
tamil_str = tamilstring.String(string)

# எழுத்துக்களைப் பிரித்தல்
characters = list(tamil_str)
print(characters)
```

**வெளியீடு:**

```python
['த', 'மி', 'ழ்']
```

For more detailed usage and advanced features, please refer to the [Documentation](https://tamilstring-011d48.gitlab.io/).

## Contributing - பங்களிப்பு

**English:**

We welcome contributions! If you have suggestions or encounter issues, please raise them in our [GitLab Issues](https://gitlab.com/boopalan-dev/tamilstring/-/issues).

**தமிழ்:**

நாங்கள் பங்களிப்புகளை வரவேற்கிறோம்! உங்களிடம் பரிந்துரைகள் அல்லது சிக்கல்கள் இருந்தால், தயவுசெய்து அவற்றை எங்கள் [GitLab Issues](https://gitlab.com/boopalan-dev/tamilstring/-/issues) இல் பதிவு செய்யவும்.

### Adding Yourself as a Contributor | பங்களிப்பாளராக சேர்க்க

**English:**

At the time of contribution, please add your profile to the list of contributors **before** sending the merge request by including the following HTML snippet in the `README.md` file:

```html
<a href="https://gitlab.com/your_username">
  <img src="IMAGE_URL" width="100" height="100" style="border-radius: 50%;" alt="Your Name"/>
</a>
```

**Instructions:**

1. Go to your GitLab profile.  
2. Right-click your profile image → “Open image in new tab”.  
3. Copy the full image URL from the new tab.  
4. Replace `IMAGE_URL` in the above snippet with the copied URL.  
5. Replace `your_username` and `Your Name` accordingly.

**தமிழ்:**

பங்களிப்பு செய்யும் போது, merge request அனுப்புவதற்கு முன் `README.md` கோப்பில் பங்களிப்பாளர்கள் பட்டியலில் உங்கள் சுயவிவரத்தை கீழ்காணும் HTML குறியீட்டின் மூலம் சேர்க்கவும்:

```html
<a href="https://gitlab.com/your_username">
  <img src="IMAGE_URL" width="100" height="100" style="border-radius: 50%;" alt="உங்கள் பெயர்"/>
</a>
```

**வழிமுறைகள்:**

1. உங்கள் GitLab சுயவிவரத்திற்கு செல்லவும்.  
2. சுயவிவரப் படத்தை வலது கிளிக் செய்து “Open image in new tab” என்பதைத் தேர்ந்தெடுக்கவும்.  
3. புதிய தாவலில் தோன்றும் URL ஐ முழுவதுமாக copy செய்யவும்.  
4. மேலே உள்ள குறியீட்டில் `IMAGE_URL` என்பதை அந்த URL உடன் மாற்றவும்.  
5. பின்னர் `your_username` மற்றும் `உங்கள் பெயர்` விவரங்களுடன் மாற்றவும்.

## License - உரிமம்

**English:**

This project is licensed under the MIT License. See the [LICENSE](https://gitlab.com/boopalan-dev/tamilstring/-/blob/main/LICENSE) file for details.

**தமிழ்:**

இந்த திட்டம் MIT உரிமத்தின் கீழ் வழங்கப்படுகிறது. விவரங்களுக்கு [உரிமம்](https://gitlab.com/boopalan-dev/tamilstring/-/blob/main/LICENSE) கோப்பை பார்க்கவும்.

## Acknowledgments - நன்றியுரைகள்

**English:**

Special thanks to all contributors and the open-source community for their invaluable support.

**தமிழ்:**

அனைத்து பங்களிப்பாளர்களுக்கும் மற்றும் திறந்த மூல சமூகத்திற்கும் அவர்களின் மதிப்புமிக்க ஆதரவுக்கு சிறப்பு நன்றி.

## Contributors - பங்களிப்பாளர்கள்

<a href="https://gitlab.com/boopalan-dev">
  <img src="https://gitlab.com/uploads/-/system/user/avatar/22134717/avatar.png?s=100" width="100" height="100" style="border-radius: 50%;" alt="Boopalan S"/>
</a>
<a href="https://gitlab.com/anandsundaramoorthysa">
  <img src="https://gitlab.com/uploads/-/system/user/avatar/22613937/avatar.png?s=100" width="100" height="100" style="border-radius: 50%;" alt="Anand Sundaramoorthy SA"/>
</a>