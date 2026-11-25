# Path.AI — Developer Guide

## 1. Project Overview

Path.AI is an *offline, on-device degree recommendation app* for graduating senior high school students in Camarines Sur.

- *Framework:* Python + Flet 1.1.2
- *Platforms:* Android (APK) and Windows
- *Architecture:* MVC
- *Runtime:* Fully offline; no server or user accounts.
- *Data:* Embedded JSON datasets and local device storage.

## 2. Frontend Architecture

The frontend must communicate with the application exclusively through PathAIController.

mermaid
flowchart TD
    V[Flet UI / View] --> C[PathAIController]
    C --> R[Repositories]
    C --> M[MatchingEngine]
    V -.-> S[StorageBackend Adapter]

*Frontend responsibilities:*
- Build screens, navigation, and UI components.
- Collect and validate user inputs.
- Call controller methods to save answers and retrieve data.
- Display recommendations and associated institutions and campuses.
- Implement the StorageBackend adapter for device storage.

*Important:* Do not directly import or access Model components. All application data must go through the controller.

## 3. Main User Flow

The application has three intake stages:

| Stage | User Inputs | Frontend Requirements |
|---|---|---|
| 1. Preferences & Profile | Tuition preference, location, relocation, scholarship, SHS strand, grade band, gender | Collect and save user information |
| 2. Traits | Six traits rated 1–5 | Display trait questions and show the top 3 recommended academic clusters |
| 3. Skills | Skills related to recommended clusters, rated 1–5 | Dynamically display relevant skills (maximum 12 items) |

*Navigation flow:*

Preferences → Traits → Recommended Clusters → Skills → Results

Save user answers immediately as they progress through the intake.

## 4. Controller API

Initialize the controller:

controller = PathAIController(storage_backend)

### Retrieve Data

| Method | Purpose |
|---|---|
| trait_catalog() | Get available trait questions |
| college_catalog() | Get academic clusters |
| top_colleges(k) | Get the highest-ranked clusters |
| skill_catalog(college_ids, k) | Get skills for selected clusters |
| locations() | Get available municipalities |
| answers() | Retrieve saved answers |
| last_results() | Retrieve previous recommendations |
| has_saved() | Check whether saved data exists |

### Save or Submit Data

| Method | Purpose |
|---|---|
| set_preferences(**kw) | Save user preferences |
| set_profile(**kw) | Save student profile |
| set_trait(key, value) | Save a trait rating (1–5) |
| set_skill(key, value) | Save a skill rating (1–5) |
| set_step(n) | Save current intake step |
| submit() | Generate and return recommendations |
| clear_my_data() | Delete all locally stored user data |

All setters persist changes immediately.

## 5. Recommendation Results

submit() returns a list of recommendation objects.

Each result contains:

| Field | Description |
|---|---|
| degree | Degree ID, name, and academic cluster |
| college | Academic cluster information |
| match_pct | Match percentage |
| rank_score | Internal ranking score |
| fit_basis | Whether matching used traits or skills |
| badges | Relevant preference indicators |
| rationale | Explanation of the recommendation |
| offerings | Institutions and campuses offering the degree |

*Frontend requirements:*
- Display the top 3 recommended degree programs.
- Show match percentages and explanations.
- Display associated institutions, municipalities, and campuses.
- Show relevant badges such as tuition-free options and preferred locations.
- Clearly distinguish institutions and their individual campuses.

## 6. Local Storage

User data is stored locally using the StorageBackend interface.

| Key | Stored Data |
|---|---|
| pathai.answers | Intake answers |
| pathai.results | Latest recommendation results |
| pathai.last_active | Last activity timestamp |

The frontend must provide the storage adapter implementing:

get(key)
set(key, value)
remove(key)
keys()

*Data retention:* Automatically remove saved data after 30 days of inactivity or when the user selects Clear My Data.

## 7. Development Constraints

- *Offline-first:* No runtime network requests or external APIs.
- *Privacy:* Student profile information (strand, grade band, gender) must never be used for recommendation scoring.
- *Controller-only access:* Never access Model components directly from the UI.
- *Read-only datasets:* Embedded reference JSON files must not be modified at runtime.
- *Cross-platform:* UI must work on Android and Windows.
- *Android compatibility:* Avoid native scientific computing dependencies.
