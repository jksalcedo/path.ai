# Path.AI - AI-assisted college program recommendation tool

**Team:** Git-Ling  
**S/Y:** 2026-2027

**Courses:**
- CCCS 106 - Application Development and Emerging Technologies
- CS 3110 - Software Engineering 1

**Members:**
- Kurt Rainier B. Aquino
- Chris Jericho Francisco
- Jaressen Kyle Salcedo

# Project Overview

Path.AI is an AI-assisted college program recommendation application built using the **Flet framework (Python + Flutter rendering)**. The system uses student profiling and a content-based recommendation approach to identify college programs and higher education institutions (HEIs) that best match a student's interests, strengths, and preferences.

Rather than relying on a single academic strength or subject proficiency, Path.AI evaluates multiple student characteristics to determine suitable academic fields and specific college programs. This allows the system to distinguish between programs with similar requirements and provide more relevant recommendations.

The application aims to help graduating senior high school students in Camarines Sur make more informed college decisions through localized, data-driven recommendations.

### Target Users

- **Senior High School Students** - Discover college programs that align with their interests, strengths, and abilities.
- **Prospective College Students** - Explore available programs and institutions across Camarines Sur.
- **Higher Education Institutions (HEIs)** - Gain visibility among students whose profiles align with their offered programs.

### Problem Statement

Choosing a college program can be challenging, especially for students who have limited access to proper career guidance. Many rely on peer influence, family pressure, or guesswork when deciding which program to pursue.

A particular challenge is identifying the specific program that best suits a student when multiple programs share similar academic requirements. For example, excelling in Mathematics may indicate potential in several fields, including Engineering, Computer Science, and Statistics, but does not necessarily determine which specific program is the best fit.

Path.AI addresses this problem by evaluating combinations of student interests, strengths, and preferences to provide more personalized program recommendations, helping students explore suitable academic paths and the institutions offering them.

## AI Recommendation Process

Path.AI uses a **two-level, content-based recommendation approach** powered by weighted scoring and potentially a lightweight machine learning classifier.

The recommendation process consists of the following stages:

1. **Student Assessment** - Students complete an intake form covering their interests, strengths, subject preferences, and optional personal preferences such as budget and preferred location.
2. **Profile Processing** - Assessment responses are converted into trait indicators, such as analytical, creative, technical, and people-oriented abilities.
3. **Field Matching** - The system identifies suitable academic fields or disciplines based on the student's overall profile.
4. **Specific Program Matching** - Individual programs within the identified fields are evaluated against the student's profile to determine their compatibility.
5. **Institution Matching** - Recommended programs are cross-referenced with the local dataset to identify the HEIs offering them.
6. **Ranked Recommendations** - The system presents suitable programs and their corresponding institutions, accompanied by compatibility scores and brief explanations.

The recommendation engine will use a manually compiled and labeled dataset of college programs and their associated trait indicators from participating HEIs in Camarines Sur. A weighted scoring approach or lightweight machine learning algorithm, such as Decision Tree or k-Nearest Neighbors (k-NN), will be used for program matching.

## Planned Features

- Personalized college program recommendations
- Multi-trait student assessment
- Two-level academic field and specific program matching
- Ranked recommendations with compatibility scores
- Explanations for recommended programs
- Information on participating HEIs in Camarines Sur
- Offline functionality and local data storage

## Tech Stack

- **Language:** Python
- **Framework:** Flet
- **Machine Learning:** scikit-learn
- **Recommendation Method:** Content-based filtering / Weighted scoring
- **Data Storage:** JSON / Local Storage

## Platform

- Android (APK)
- Windows Desktop

## Privacy

- No user accounts or login required.
- Student profiles and assessment responses are stored locally on the device.
- Recommendation processing runs entirely on-device.
- No external AI API or cloud-based inference service is required.

## Project Status

Currently under development.

## Running Tests

Install the test dependency and run the test suite:

```bash
python -m pip install -r requirements-dev.txt
python -m pytest
```

GitHub Actions runs pytest for every pull request.

---

*Path.AI - Helping students find a college path that fits them.*
