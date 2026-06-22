# FitFindr — Starter Kit

This starter kit contains everything you need to begin Project 2.

## What's Included

```
ai201-project2-fitfindr-starter/
├── data/
│   ├── listings.json          # 40 mock secondhand listings
│   └── wardrobe_schema.json   # Wardrobe format + example wardrobe
├── utils/
│   └── data_loader.py         # Helper functions for loading the data
├── planning.md                # Your planning template — fill this out first
└── requirements.txt           # Python dependencies
```

## Setup

```bash
pip install -r requirements.txt
```

Set your Groq API key in a `.env` file (get a free key at [console.groq.com](https://console.groq.com)):
```
GROQ_API_KEY=your_key_here
```

## The Mock Listings Dataset

`data/listings.json` contains 40 mock secondhand listings across categories (tops, bottoms, outerwear, shoes, accessories) and styles (vintage, y2k, grunge, cottagecore, streetwear, and more).

Each listing has: `id`, `title`, `description`, `category`, `style_tags`, `size`, `condition`, `price`, `colors`, `brand`, and `platform`.

Load it with:
```python
from utils.data_loader import load_listings
listings = load_listings()
```

## The Wardrobe Schema

`data/wardrobe_schema.json` defines the format your agent uses to represent a user's existing wardrobe. It includes:

- `schema`: field definitions for a wardrobe item
- `example_wardrobe`: a sample wardrobe with 10 items you can use for testing
- `empty_wardrobe`: a starting template for a new user

Load an example wardrobe with:
```python
from utils.data_loader import get_example_wardrobe
wardrobe = get_example_wardrobe()
```

## Where to Start

1. **Read `planning.md` and fill it out before writing any code.**
2. Verify the data loads correctly by running `python utils/data_loader.py`.
3. Build and test each tool individually before connecting them through your planning loop.

Your implementation files go in this same directory. There's no required file structure for your agent code — organize it however makes sense for your design.
## Tools

List every tool your agent will use. For each tool, fill in all four fields.
You must have at least 3 tools. The three required tools are listed — add any additional tools below them.

### Tool 1: search_listings

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
searches the database looking for the best matches based on criteria. picks the best match as the top pick. 

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `description` (str): description of item, represents what the query should look for in the database.
- `size` (str): represents the size of the item the user is looking for , 
- `max_price` (float): represents the max price of item the user is looking for, should use the price field of the item entry to find prices that are below this


**What it returns:**
<!-- Describe the return value — what fields does a result contain? -->
returns the top item that matches what the user is looking for.

**What happens if it fails or returns nothing:**
<!-- What should the agent do if no listings match? -->
if nothing is found , tell the user to suggest a new item , do not call suggest_outfit or create_fit_card

---

### Tool 2: suggest_outfit

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
suggests other items that would look good with the item. uses the new item that found and the current users warddrobe. if the user has no wardrobe yet , create one and then put the item in there. if user provided list of other items they wear use those otherwise use whats in the wardrobe.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `new_item` (dict): ...
- `wardrobe` (dict): ...

**What it returns:**
<!-- Describe the return value -->
returns a suggestion, if no wardrobe uses any items listed in input otherwise uses items already in the wardrobe

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the wardrobe is empty or no outfit can be suggested? -->
if the wardrobe is empty add the item to the wardrobe, tell the user to continue adding more item to the wardrobe. 

---

### Tool 3: create_fit_card

**What it does:**
<!-- Describe what this tool does in 1–2 sentences -->
uses wardrobe and last fetched item to build a social media post like string.

**Input parameters:**
<!-- List each parameter, its type, and what it represents -->
- `outfit` (dict): current suggestions 
- 'new item' (dict): gets last item.

**What it returns:**
<!-- Describe the return value -->
returns a string based on what in the wardrobe 

**What happens if it fails or returns nothing:**
<!-- What should the agent do if the outfit data is incomplete? -->
if data is incomplete ask user to continue chatting so we can add more items and build a suggestion.
---

### Additional Tools (if any)

<!-- Copy the block above for any tools beyond the required three -->

---

## Planning Loop

**How does your agent decide which tool to call next?**
<!-- Describe the logic your planning loop uses. What does it look at? What conditions change its behavior? How does it know when it's done? -->

After search_listings runs, check if results is empty. If yes, set an error message in the session and return early. If no, set selected_item = results[0]
input results[0] if not null into suggest_outfit along with the current wardrobe. if wardrobe is empty or null create it, have the agent use the input if the wardrobe is empty or incomplete ( need at least a shirt ( its called tops in the item category section ) and pants ( bottoms in the category section of item )).
if all theres at least one item in the wardrobe for each category use all those otherwise ( one tops and one bottoms) use all of those otherwise use the users input. 
use the suggestion if its not null, use it as an input for create_fit_card along with the item suggested. if both are null, stop and return error message to user . return a string that uses the suggestion and item. should feel like a social media post.

---

## State Management

**How does information from one tool get passed to the next?**
<!-- Describe how your agent stores and accesses state within a session. What data is tracked? How is it passed between tool calls? -->
use a results variable to add on the the results, should be global and be used by the above functions to grab user inputs. 

---

## Error Handling

For each tool, describe the specific failure mode you're handling and what the agent does in response.

| Tool | Failure mode | Agent response |
|------|-------------|----------------|
| search_listings | No results match the query | return error message |
| suggest_outfit | Wardrobe is empty | return message , start new wardrobe |
| create_fit_card | Outfit input is missing or incomplete | use prompt to suggest outfits |

---

## Architecture

<!-- Draw a diagram of your agent showing how the components connect:
     User input → Planning Loop → Tools (search_listings, suggest_outfit, create_fit_card)
                                                                          ↕
                                                                   State / Session
     Show what triggers each tool, how state flows between them, and where error paths branch off.
     ASCII art, a Mermaid diagram (https://mermaid.js.org/syntax/flowchart.html), or an embedded
     sketch are all fine. You'll share this diagram with an AI tool when asking it to implement
     the planning loop and each individual tool. -->

'''mermaid
---
config:
  layout: dagre
---
flowchart TD
    Start[User Query] --> PlanningLoop[Planning Loop]
    
    subgraph Planning Loop
        Search[search_listings<br/>description, size, max_price]
        CheckResults{results empty?}
        
        ErrorSearch[Session: error_msg = No listings found...]
        SetSelected["Session: selected_item = results[0]"]
        
        Suggest[suggest_outfit<br/>selected_item, wardrobe]
        HandleWardrobe{Wardrobe check}
        
        CreateWardrobe["Create / init wardrobe<br/>using user input if empty or incomplete<br/>(need ≥1 tops + ≥1 bottoms)"]
        UseWardrobe["Use all wardrobe items<br/>(tops + bottoms)"]
        UseInput[Use user input item]
        
        CreateCard[create_fit_card<br/>outfit_suggestion, selected_item]
        CheckInputs{Both null?}
        
        ErrorCard[Session: error_msg = Missing outfit or item]
        BuildPost[Build social media style post<br/>using suggestion + item]
        SessionUpdate[Update Session:<br/>fit_card = post_string]
    end
    
    Return[Return Session]
    
    Start --> Search
    Search --> CheckResults
    CheckResults -- Yes --> ErrorSearch --> Return
    CheckResults -- No --> SetSelected --> Suggest
    
    Suggest --> HandleWardrobe
    HandleWardrobe -- empty/null or incomplete --> CreateWardrobe --> Suggest
    HandleWardrobe -- has tops + bottoms --> UseWardrobe --> Suggest
    HandleWardrobe -- otherwise --> UseInput --> Suggest
    
    Suggest --> CreateCard
    CreateCard --> CheckInputs
    CheckInputs -- Yes --> ErrorCard --> Return
    CheckInputs -- No --> BuildPost --> SessionUpdate --> Return


'''

---

## AI Tool Plan

<!-- For each part of the implementation below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, your agent diagram)
     - What you expect it to produce
     - How you'll verify the output matches your spec before moving on

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Tool 1 spec (inputs, return value, failure mode) and ask it to implement
     search_listings() using load_listings() from the data loader — then test it against 3 queries
     before trusting it" is a plan. -->
i used claude code to develop the tools as instructed from planning.md. i gave it each section required by each function to create the function implementaion and gave the functions as needed. i was expecting it to produce 100% working functions but sadly that was not the case. i ran the app once all the functions were implemented and fixed various errors such as claude code changing parameters and calling the LLM at weird times. fixing issues with error handling. i verified that all the required behavior was occurring in each function before moving on to the next stage. 

another instance where i used ai ( claude ) is in the testing part. i provided it the examples listed but i underspecifed how it should create the tests. it was creating its own example wardrobes and calling the LLM in the tests which it couldnt do. i had to edit or remove ones that were testing the LLM itself rather than the functions. 

# A Complete Interaction (Step by Step)

Write out what a full user interaction looks like from start to finish — tool call by tool call. Use a specific example query.

**Example user query:** "I'm looking for a vintage graphic tee under $30. I mostly wear baggy jeans and chunky sneakers. What's out there and how would I style it?"

**Step 1:**
<!-- What does the agent do first? Which tool is called? With what input? -->
agent uses search_listings to find a match for the item the user is looking for. uses the top search result as the top pick. input: vintage teee , under $30, uses other words in the input to find the best match.

**Step 2:**
<!-- What happens next? What was returned from step 1? What tool is called now? -->
uses the item that was suggested from step one and the original query as input and calls suggest_outift, returns outfits that match what the user is looking for. adds outfit to fit card. if its the first time it creates a new one using create_fit_card
if not outfit found ask the user to suggest something else. do not add empty to fit card 
**Step 3:**
<!-- Continue until the full interaction is complete -->

**Final output to user:**
<!-- What does the user actually see at the end? -->
updates fit card and builds wardrobe for user


# reflections
i did think of other errors that i did not think of during debugging and building out the program.
