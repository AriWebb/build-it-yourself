# Build It Yourself

Transform your Python code by removing external dependencies and building functionality from scratch. This tool helps developers understand and recreate the functionality of external dependencies in their own codebase. The current functionality is very limited, but it is a start. There are many ideas for improvements and features to be added in the future.

## Motivation

A couple of weeks ago, I read a [blog post I found on HN](https://lucumr.pocoo.org/2025/1/24/build-it-yourself/) lamenting how modern software engineering emphasizes usage of external dependencies. In my view, there are a few problems with overuse of external dependencies:

1. Dependency management is hard. Especially as projects get larger, dependency management becomes such a headache. Upgrades break code. Over time, code with too many dependencies is virtually guaranteed to break. What if we want our code to work over long periods of time without engineer intervention?
2. Security issues. External dependencies can introduce supply chain vulnerabilities.
3. Performance issues. External dependencies can slow down development processes.

I thought LLMs could help generate dependency free code, so I built this tool that takes short Python code snippets with dependencies and generates code that inlines the dependencies.

Of course, dependency usage has its benefits too. Complex libraries, and things that must change over time are often best outsourced to third party libraries. Further, there is no need to inline dependencies that stay relatively static over time.

## Project Structure

The project is organized into two main components:

- `frontend/`: Next.js web application that provides the user interface
- `backend/`: Python backend (FastAPI) that analyzes dependencies and provides transformation suggestions

## Features

- Dependency Analysis: Identifies external dependencies in your Python code, fetches them and finds the function definitions that are called in your code.
- Code Transformation: Uses Claude API to rewrite code without external dependencies
- Modern Web Interface: Clean and intuitive UI built with Next.js

## Getting Started

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install Python dependencies:
```bash
make init
```

3. Set your anthropic API key:
```bash
export ANTHROPIC_API_KEY="your-api-key"
```

4. Start the backend server:
```bash
make run
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd frontend
```

2. Install Node.js dependencies:
```bash
npm install
```

3. Start the development server:
```bash
npm run dev
```

The application will be available at `http://localhost:3000`.

## Usage

1. Paste your Python code into the web interface and click submit.
2. The tool will analyze your code for non-basic external dependencies, fetch them, and find the function definitions that are called in your code.
3. It then takes this information and uses the Claude API to rewrite your code, inlining the external dependencies. 

## Development

### Tests

Unit testing the dependency resolver is less difficult than outputted code, as the code comes from Claude. I haven't made too many test cases yet, but there are a couple there. Expanding this suite could be helpful to figure out the effectiveness of improvmeents to prompting and dependency resolution.

For backend tests:
```bash
cd backend
make test
```

## Potential Improvements
1. Improve the prompting. The current prompting is pretty basic, and I think that we could get better results through maybe chunking the output from the resolver and using that to generate more targeted prompts, then weave the ouput together.
2. Improve the dependency resolving capability. It is difficult to get the regexes correct to make sure when find all references. I tried to cover more basic cases but there are definitly more edge cases I haven't covered.
3. Let the user choose dependencies/functions to inline. We might not want to inline everything, and instead just focus on a few specific parts of code.
4. Recursive dependency resolution. We want to collect the dependencies of the depenencies, and so on. This, of course, exponentially increases the amoun of code to rewrite. But, I think this is also where a lot of the value add is unlocked.
5. Scale this up. Pretty self-explanatory. Being able to do this to a large file or even a whole project could be super cool. With the current prompting setup, it can only do very small files.
6. Do other langauges. The methodology is the same, but the regexes for searching through packages will obviously need to be different. The author of Build It Yourself mentioned that Rust has this dependency problem too, so that might be a cool place to go. 

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request or improve on this codebase on your own. I believe this is a cool idea to pursue, but am unsure how much more I will personally build on it.
