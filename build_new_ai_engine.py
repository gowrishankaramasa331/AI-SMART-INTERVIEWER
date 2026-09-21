"""
Script to create the enhanced ai_engine.py with massive question bank expansion
and dynamic adaptive question generation.
"""
import os

code = '''"""
AI Smart Interview System — AI Engine
Handles question generation, answer evaluation, and dynamic adaptive questioning
using Google Gemini API with a comprehensive built-in semantic fallback.
"""
import json
import random
import re
from config import GEMINI_API_KEY

# ── Try to import Gemini ──────────────────────────────────
genai = None
if GEMINI_API_KEY:
    try:
        import google.generativeai as _genai
        _genai.configure(api_key=GEMINI_API_KEY)
        genai = _genai
        print("[AI Engine] Gemini API configured successfully.")
    except Exception as e:
        print(f"[AI Engine] Gemini API init failed: {e}. Using fallback.")
else:
    print("[AI Engine] No GEMINI_API_KEY set. Using built-in question bank.")


# ═══════════════════════════════════════════════════════════
#  EXPANDED BUILT-IN QUESTION BANK (Comprehensive)
# ═══════════════════════════════════════════════════════════

QUESTION_BANK = {
    "hr": {
        "easy": [
            "Tell me about yourself and your professional background.",
            "Why are you interested in joining our organization?",
            "What do you consider your greatest personal and technical strengths?",
            "What is an area of weakness you have actively worked to improve?",
            "Where do you see yourself in your career 3 to 5 years from now?",
            "Why should we choose you over other qualified candidates?",
            "Describe your ideal work environment and company culture.",
            "What motivates you to do your best work every day?",
            "How do you manage stress and maintain focus during high-pressure situations?",
            "Tell me about a time you worked productively in a multidisciplinary team.",
            "What are your salary expectations and career development goals?",
            "Do you prefer working independently, collaboratively, or in a hybrid model?",
            "What values are most important to you in an employer?",
            "How do you stay organized when juggling multiple daily tasks?",
            "What sparked your passion for your chosen field?",
            "Describe a time you received positive recognition for your work.",
            "How do you prefer to receive feedback from your manager?",
            "Tell me about a hobby outside of work that helps you stay balanced.",
            "What does good work-life balance mean to you?",
            "How do you prepare for starting a new role with a new team?",
        ],
        "medium": [
            "Tell me about a time a project failed or didn't meet expectations, and what you learned from it.",
            "Describe a situation where you had a disagreement with a coworker. How did you handle it?",
            "How do you handle a sudden change in project priorities or requirements midway through?",
            "Describe your leadership or mentorship style when collaborating with junior team members.",
            "How do you prioritize your deliverables when faced with competing, urgent deadlines?",
            "Tell me about a time you went above and beyond your defined job responsibilities.",
            "How would you handle a situation where you strongly disagree with a decision made by your manager?",
            "Describe your approach to giving and receiving constructive feedback.",
            "Tell me about a time you had to learn an unfamiliar technology or framework very quickly.",
            "How do you maintain team morale and engagement during long, challenging sprints?",
            "Describe a time you had to deal with an unhappy client, stakeholder, or user.",
            "How do you make decisions when you have incomplete or ambiguous information?",
            "Tell me about a time you persuaded a reluctant teammate to adopt your point of view.",
            "Describe how you handle burnout or prolonged periods of intense project pressure.",
            "Tell me about an instance where you identified an operational inefficiency and fixed it.",
            "How do you balance achieving high quality with meeting strict delivery deadlines?",
            "Describe a time you had to deliver critical feedback to a colleague.",
            "Tell me about a situation where you had to adapt your communication for different audiences.",
            "How do you build trust quickly with new coworkers or remote stakeholders?",
            "Describe a time you took calculated initiative on a project without waiting for direction.",
        ],
        "hard": [
            "Tell me about a time you had to make a high-stakes ethical decision at work.",
            "How would you handle a situation where an entire team is underperforming despite your coaching?",
            "Describe a time you had to influence senior executives or stakeholders to change an important strategic decision.",
            "How do you build a cohesive culture and foster psychological safety in a fully distributed remote team?",
            "Tell me about a time you had to deliver painful news (e.g. project cancellation, budget cut) to a client or team.",
            "How would you navigate deep cultural differences or communication friction in an international global team?",
            "Describe a situation where you had to balance disruptive innovation against strict compliance or risk constraints.",
            "How do you manage underperformance in a direct report who is well-liked by the entire team?",
            "Tell me about a systemic organizational bottleneck you diagnosed and successfully re-engineered.",
            "How would you handle a situation where company executive values directly conflict with day-to-day business metrics?",
            "Describe a time you were forced to make a major technical or business tradeoff that caused significant pushback.",
            "Tell me about a situation where you took full accountability for a failure that was primarily caused by your team.",
            "How do you maintain strategic long-term vision while putting out daily operational fires?",
            "Describe a time you successfully managed a project that had conflicting mandates from two different executives.",
            "How do you mentor high-performing individuals so they stay motivated without outgrowing the team too quickly?",
        ],
    },
    "technical": {
        "easy": [
            "What is the difference between a stack and a queue, and what are their typical use cases?",
            "Explain what an API is and how client-server communication works.",
            "What is the difference between HTTP and HTTPS, and how does encryption protect data?",
            "What is a relational database and why would you choose it over flat files?",
            "Explain the fundamental difference between frontend and backend software development.",
            "What is version control, and why is Git universally adopted in software development?",
            "What is the difference between a compiled language and an interpreted language?",
            "Explain the four foundational pillars of Object-Oriented Programming (OOP).",
            "What is the purpose of a constructor in a class, and when is it invoked?",
            "What are the core primitive data types in Python or JavaScript, and how are they stored?",
            "What is the difference between SQL and NoSQL databases?",
            "Explain what a RESTful API is and what HTTP methods it typically employs.",
            "What is the purpose of indexing in a database table?",
            "What is a primary key versus a foreign key in database design?",
            "Explain what CSS Flexbox and Grid are used for in modern web layouts.",
            "What is the difference between synchronous and asynchronous programming?",
            "What is a JSON file and why is it preferred over XML for web data exchange?",
            "What does the term 'DRY' (Don't Repeat Yourself) mean in software engineering?",
            "Explain what recursion is and why a base condition is mandatory.",
            "What is the difference between local variables and global variables?",
        ],
        "medium": [
            "Explain the SOLID principles of object-oriented software design with concrete examples.",
            "What is the difference between a process and a thread, and how do they share memory?",
            "Explain how a hash map (hash table) works internally, including collision resolution and time complexity.",
            "What are design patterns? Explain the Singleton, Factory, and Observer patterns.",
            "Explain the concept of database normalization (1NF, 2NF, 3NF) and when you might intentionally denormalize.",
            "What is the difference between TCP and UDP, and what applications require each?",
            "Explain the Model-View-Controller (MVC) architectural pattern.",
            "What is the difference between authentication and authorization, and how do JWT tokens fit in?",
            "Explain how garbage collection works in modern runtimes like Java, Python, or V8.",
            "What are microservices, and what are their architectural pros and cons compared to monoliths?",
            "Explain the CAP theorem and what it means for distributed data stores.",
            "What is a deadlock in concurrent systems, and what are the four conditions required for one to occur?",
            "Explain how CORS (Cross-Origin Resource Sharing) works and how to resolve CORS errors securely.",
            "What is the difference between optimistic locking and pessimistic locking in database transactions?",
            "Explain the concept of connection pooling in database-backed applications.",
            "What is the difference between horizontal scaling and vertical scaling?",
            "Explain how caching strategies like Cache-Aside, Write-Through, and Write-Back work.",
            "How does the JavaScript event loop handle microtasks (Promises) versus macrotasks (setTimeout)?",
            "What is the difference between deep copying and shallow copying of data objects?",
            "Explain what Docker containerization accomplishes that traditional virtual machines cannot.",
        ],
        "hard": [
            "Explain the internal implementation of a B+ Tree and why databases utilize it for disk-based indexing.",
            "How would you design a distributed URL shortening service (like bit.ly) handling 50,000 writes per second?",
            "Explain the Raft or Paxos consensus algorithm and how distributed leader election operates.",
            "How do modern generational garbage collectors detect and eliminate circular memory references without stopping the world?",
            "Design a distributed rate-limiting system capable of handling 10 million requests per second with low latency.",
            "Explain how container orchestration works in Kubernetes, covering kube-scheduler, etcd, and pods.",
            "Explain the architectural mechanisms behind Event Sourcing and CQRS (Command Query Responsibility Segregation).",
            "How would you design a real-time notification infrastructure delivering millions of push messages with deduplication?",
            "Explain how modern JIT compilers (like Java HotSpot or V8) optimize bytecode via profile-guided optimization.",
            "How would you implement a distributed caching layer (like Redis cluster) maintaining consistency across multi-region datacenters?",
            "Explain how database transactions achieve ACID guarantees using Write-Ahead Logging (WAL) and 2-Phase Commit (2PC).",
            "How would you design a distributed message broker (like Apache Kafka) guaranteeing partitioned ordering and fault tolerance?",
            "Explain how zero-knowledge proofs and asymmetric cryptography establish trust without revealing underlying data.",
            "How do you design a database schema and partitioning strategy to support multi-tenant SaaS applications at massive scale?",
            "Explain how memory barriers, CPU cache coherence protocols (MESI), and memory visibility impact high-frequency concurrent algorithms.",
        ],
    },
    "coding": {
        "easy": [
            "How would you reverse a string in-place in your preferred programming language?",
            "Write an algorithm to determine if a given integer is a prime number.",
            "How would you find the maximum and minimum elements in an unsorted array in a single pass?",
            "Explain how you would write a function to verify if a string is a palindrome, ignoring casing and spaces.",
            "How would you remove duplicate elements from an array without altering its relative order?",
            "Write a function to calculate the factorial of a number iteratively and recursively.",
            "How would you count the frequency of each character in a given string?",
            "Explain the approach to merge two already-sorted arrays into a single sorted array.",
            "How would you implement a simple calculator supporting basic arithmetic operations (+, -, *, /)?",
            "Write a function to find the second largest number in an unsorted integer array.",
            "How do you find the missing number in an array containing numbers from 1 to N?",
            "Write an algorithm to check if two strings are anagrams of each other.",
            "How would you count the number of vowels and consonants in a string?",
            "Explain how to check if a year is a leap year programmatically.",
            "How would you rotate an array to the right by K positions?",
            "Write a function to compute the Nth Fibonacci number efficiently using dynamic programming.",
            "How would you check if an array is sorted in ascending order?",
            "Write a function to find the intersection of two integer arrays.",
            "How do you convert a Roman numeral string into an integer value?",
            "Explain how to implement string compression (e.g. 'aabcccccaaa' -> 'a2b1c5a3').",
        ],
        "medium": [
            "How would you implement a function to find all unique pairs in an array that sum to a target value in O(N) time?",
            "Explain your approach to implement a binary search algorithm on a sorted rotated array.",
            "How would you detect a cycle in a singly linked list using Floyd's Tortoise and Hare algorithm?",
            "Write a function to find the length of the longest substring without repeating characters.",
            "How would you design and implement a Least Recently Used (LRU) cache with O(1) get and put operations?",
            "Explain your approach to solve the N-Queens problem using backtracking.",
            "How would you implement Breadth-First Search (BFS) and Depth-First Search (DFS) for a graph?",
            "Write a function to serialize and deserialize a binary tree.",
            "How would you find the shortest path in an unweighted directed graph?",
            "Explain your approach to implement a Prefix Tree (Trie) supporting insert, search, and startsWith.",
            "Write a function to solve the 0/1 Knapsack problem using dynamic programming.",
            "How would you reverse a singly linked list iteratively and recursively?",
            "Explain how to validate whether a binary tree is a valid Binary Search Tree (BST).",
            "How would you find the lowest common ancestor (LCA) of two nodes in a binary tree?",
            "Explain how you would merge overlapping intervals in an array of time ranges.",
            "How would you implement a Min-Heap or Max-Heap from scratch using an array?",
            "Write a function to generate all valid combinations of N pairs of parentheses.",
            "How would you implement QuickSort and what pivot selection strategies avoid O(N^2) worst-case time?",
            "Explain how to find the contiguous subarray with the largest sum (Kadane's Algorithm).",
            "How would you search for an element in a 2D matrix where each row and column is sorted?",
        ],
        "hard": [
            "How would you implement a thread-safe producer-consumer bounded queue with synchronization primitives?",
            "Explain your approach to solve the Traveling Salesperson Problem using branch-and-bound or dynamic programming with bitmasks.",
            "How would you implement a reference-counting garbage collector with cycle detection in C++ or Rust?",
            "Write an algorithm to compute the maximum network flow using the Ford-Fulkerson or Edmonds-Karp algorithm.",
            "How would you implement a self-balancing AVL Tree or Red-Black Tree with rotation operations?",
            "Explain your approach to design and implement a regular expression parsing and matching engine supporting '.' and '*'.",
            "How would you implement a consistent hashing ring with virtual nodes for distributed data partitioning?",
            "Write an optimized algorithm to solve an arbitrary 9x9 Sudoku board using constraint propagation and backtracking.",
            "How would you implement a Skip List supporting insert, search, and delete in O(log N) expected time?",
            "Explain your approach to implement the Lempel-Ziv-Welch (LZW) or Huffman data compression algorithm.",
            "How would you find the Median of Two Sorted Arrays of different sizes in O(log(min(M, N))) time?",
            "How would you design an algorithm to find strongly connected components in a directed graph using Tarjan's or Kosaraju's algorithm?",
            "Explain how to implement an inverted index search engine with TF-IDF relevance scoring in memory.",
            "How would you implement lock-free concurrent data structures using Compare-And-Swap (CAS) atomic operations?",
            "Write an algorithm to compute the edit distance (Levenshtein distance) between two long sequences in optimized memory space.",
        ],
    },
    "communication": {
        "easy": [
            "How would you explain your favorite technology or tool to someone with no computer background?",
            "How do you introduce yourself professionally in 60 seconds during an introductory client meeting?",
            "Describe a technical project you built using simple, jargon-free analogies.",
            "How do you prepare your speaking points and visual slides before delivering an important presentation?",
            "What core qualities distinguish an exceptional communicator from an average communicator in engineering teams?",
            "How do you break down complex, multi-layered technical concepts so non-technical colleagues understand?",
            "Describe how you structure constructive feedback to a teammate so they feel encouraged rather than criticized.",
            "What rules do you follow to ensure your daily Slack, Teams, or email messages are concise and actionable?",
            "What do you do in a high-stakes technical meeting when you don't understand a term someone mentions?",
            "How would you summarize a 20-page technical whitepaper into three bullet points for an executive?",
            "How do you confirm that another person has clearly understood the instructions you just provided?",
            "Describe a time you had to clarify ambiguous project requirements by asking targeted questions.",
            "How do you keep attendees engaged and on-topic when running a virtual standup or meeting?",
            "What is your approach to writing clear, clean pull request descriptions and Git commit messages?",
            "How do you introduce a new tool or library to your team to convince them it is worth testing?",
            "Describe how you handle interruptions respectfully during team discussions.",
            "How do you communicate project status updates when progress has been slower than planned?",
            "What role does body language and vocal inflection play in virtual or in-person interviews?",
            "How do you adapt your communication when speaking with a designer versus a backend engineer?",
            "Describe how you share daily learnings or tips with your peers.",
        ],
        "medium": [
            "How would you handle a situation where an idea you spent weeks researching was immediately rejected in a team meeting?",
            "Describe how you would present a major technical refactoring proposal to non-technical business stakeholders.",
            "How do you adapt your tone and communication style when delivering bad news versus celebrating a victory?",
            "Tell me about a time when miscommunication caused a bug or delay, and how you resolved the root issue.",
            "How would you deliver an engaging 5-minute lightning talk on a technology topic you discovered yesterday?",
            "Describe your approach to active listening during high-friction technical debates.",
            "How do you handle unexpected or aggressive questions from executives during an architecture review?",
            "What strategies do you use to persuade skeptical colleagues to adopt modern best practices like automated testing?",
            "How would you proactively communicate an unavoidable project delay to clients without losing their confidence?",
            "Describe how you document internal system architecture so new team members can onboard independently in days.",
            "How do you handle a teammate who dominates discussions and rarely allows quiet engineers to speak?",
            "Describe a time you had to deliver difficult feedback upward to your manager or team lead.",
            "How do you communicate trade-offs when business leaders demand all features delivered immediately?",
            "Tell me about a time you translated customer complaints into concrete engineering tasks for developers.",
            "How do you conduct post-mortems after a production incident to ensure blameless learning?",
            "Describe how you present data metrics or KPI results so that non-technical leaders can make decisions.",
            "How do you facilitate consensus when two senior engineers have conflicting architectural proposals?",
            "Tell me about a time you had to communicate with an upset customer whose workflow was disrupted by a software outage.",
            "How do you bridge communication gaps between remote team members working in completely different time zones?",
            "Describe how you create an open, safe environment where junior team members feel comfortable asking basic questions.",
        ],
        "hard": [
            "How would you mediate an intense, emotional conflict between two senior leads with diametrically opposed technical visions?",
            "Describe your strategy for announcing a massive corporate restructuring or tech migration to a team anxious about their jobs.",
            "How would you manage communication during a critical P0 security breach or customer data leak crisis?",
            "Explain how you build lasting trust, mutual empathy, and operational rhythm across globally distributed, multi-cultural teams.",
            "How would you deliver a compelling, inspiring keynote presentation to an auditorium of 1,000 industry professionals?",
            "Describe your methodology for navigating cross-cultural communication nuances in multinational corporate mergers.",
            "How would you communicate a controversial corporate policy change (such as strict return-to-office) while retaining top engineers?",
            "How would you handle a viral social media PR crisis regarding an algorithmic bias or service failure in your product?",
            "How do you establish transparent, frictionless communication between engineering, marketing, legal, and executive teams?",
            "Describe how you coach a technically brilliant developer whose abrasive communication style is alienating the rest of the team.",
            "How do you maintain team trust when you are bound by NDA or confidentiality and cannot disclose all details of an executive decision?",
            "Describe how you negotiate high-stakes SLAs and service contracts with difficult enterprise client executives.",
            "How do you present an uncomfortable truth to a CEO when project metrics prove their pet initiative is failing?",
            "What framework do you use to ensure information cascading reaches the frontline engineers accurately without dilution?",
            "Describe a time you transformed a toxic, blame-heavy team culture into a transparent, empathetic engineering community.",
        ],
    },
    "general": {
        "easy": [
            "What originally inspired you to pursue a career in technology and computer science?",
            "What is your favorite personal or academic project you have built, and why?",
            "How do you stay updated with emerging technology trends, AI advances, and industry best practices?",
            "What books, podcasts, or online resources have had the greatest positive impact on your thinking?",
            "Describe your ideal job role, day-to-day responsibilities, and long-term career trajectory.",
            "What extracurricular activities, open-source work, or hackathons have you participated in?",
            "How do you balance your time effectively between coursework, projects, and personal life?",
            "What new technical and professional skills do you plan to master over the next 12 months?",
            "Tell me about a personal hobby or interest that has taught you valuable professional skills.",
            "What is the single most valuable lesson you learned during your college education?",
            "How do you decide what programming language or framework to learn next?",
            "What does professional integrity mean to you in the context of building software?",
            "Describe a time you taught yourself a difficult concept completely independently.",
            "What role do you usually take on when working in a group of your peers?",
            "What is your proudest non-academic or non-technical achievement to date?",
            "How do you stay motivated when working on repetitive or tedious assignments?",
            "What kind of company mentorship program would benefit you most at this stage in your career?",
            "How do you handle unfamiliar bugs that have no immediate answers on Stack Overflow or Google?",
            "What are your favorite developer tools (IDE, terminal, extensions) and why?",
            "If you could build any software application without budget or time constraints, what would you create?",
        ],
        "medium": [
            "How has the rapid rise of Artificial Intelligence and automation changed your perspective on software development?",
            "Describe a situation where you had to master a complex technology stack from scratch under tight deadlines.",
            "What is your stance on the balance between theoretical computer science concepts and practical hands-on development?",
            "If you could go back to the start of your higher education, what would you do differently to maximize your growth?",
            "How do you systematically approach debugging when you are completely stuck and standard tools offer no clues?",
            "Describe a significant setback or failure in your past, and the exact process you used to recover and grow from it.",
            "What is your framework for evaluating whether an emerging technology is a permanent breakthrough or just temporary hype?",
            "What role does creative and lateral thinking play in solving difficult software engineering challenges?",
            "How do you assess the technical debt of a project versus the urgent commercial need to ship new features?",
            "What strategies do you use to maintain deep focus and prevent distractions in a hyper-connected workplace?",
            "How do you decide when a piece of software is 'good enough' to deploy versus spending more time perfecting it?",
            "Describe an experience where you had to quickly adapt your working style to a team with very different habits.",
            "What is your perspective on open source contribution, and how has the open source ecosystem shaped your skills?",
            "How do you approach learning complex codebases written by other developers without existing documentation?",
            "Describe a situation where you took a calculated risk on an unconventional solution, and what the outcome was.",
            "How do you ensure that the code you write today remains readable, maintainable, and extensible for future developers?",
            "What ethical responsibilities do software engineers bear when building algorithms that influence human behavior?",
            "How do you measure your own personal productivity and progress as a developer week over week?",
            "Tell me about a time you identified a bug in production before users reported it, and how you managed the resolution.",
            "What advice would you give to a first-year student starting out in your field?",
        ],
        "hard": [
            "How do you envision the long-term societal and economic implications of autonomous AI agents in engineering?",
            "What is the single greatest structural vulnerability or challenge the software industry will face in the next 10 years?",
            "If you were granted $1M in seed funding to launch a technology startup today, what problem would you solve and how?",
            "How should higher education and university curricula evolve to prepare engineers for an AI-augmented future?",
            "How do you reconcile the pursuit of rapid technical innovation with long-term ecological and energy sustainability?",
            "What architectural or systemic changes would you propose to democratize access to high-performance computing globally?",
            "How do you formulate a concrete plan of attack when tasked with solving a problem that has no existing industry precedent?",
            "What is the future of open-source software monetization, and how do we protect maintainers from burnout and exploitation?",
            "How do you quantify and strategically pay down technical debt across enterprise systems without halting product feature velocity?",
            "Describe your cognitive framework for making irreversible high-stakes technical decisions in the face of acute uncertainty.",
            "How do you evaluate the trade-off between user data privacy and the data requirements needed to train intelligent systems?",
            "What principles should govern the deployment of artificial intelligence in safety-critical systems like healthcare and aviation?",
            "How do you architect a software organization to remain agile and innovative even as it grows past thousands of engineers?",
            "In an era where code generation is largely automated, what will be the core differentiator of elite software architects?",
            "How do you instill a culture of rigorous security and resilience from day one rather than treating it as an afterthought?",
        ],
    },
}

# ═══════════════════════════════════════════════════════════
#  ADAPTIVE TOPIC KNOWLEDGE BASE (For Fallback Q2+ Synthesis)
# ═══════════════════════════════════════════════════════════

ADAPTIVE_TOPIC_QUESTIONS = {
    # ── Frontend & Web ──
    "react": [
        "You discussed using React. How did you manage component state and side effects, and why did you choose that approach over Context API or Redux?",
        "Following up on your experience with React: how do you prevent unnecessary re-renders and optimize virtual DOM performance in high-frequency update scenarios?",
        "When building React applications, what is your approach to component modularity, custom hooks, and testing with tools like Jest or React Testing Library?",
        "How do you handle client-side routing, code-splitting, and lazy loading in React applications to maintain lightning-fast initial page loads?",
    ],
    "javascript": [
        "Building on what you mentioned about JavaScript: how does the asynchronous event loop handle heavy I/O operations without blocking the single execution thread?",
        "You discussed JavaScript. How do closures and lexical scoping work under the hood, and what is a practical scenario where you utilized them?",
        "In JavaScript, how do you handle error propagation across asynchronous Promises and async/await chains to prevent unhandled rejections?",
        "What are the key performance differences between prototypal inheritance in JavaScript and classical OOP languages like Java or C++?",
    ],
    "typescript": [
        "You mentioned TypeScript. What are the key advantages of TypeScript's static typing and generics in preventing runtime production bugs?",
        "In TypeScript, how do you utilize advanced types like union types, mapped types, and utility types (e.g. Partial, Pick) to keep code DRY and safe?",
    ],
    "frontend": [
        "You touched on frontend development. How do you ensure cross-browser compatibility, accessible WCAG compliance, and responsive layouts across viewports?",
        "What strategies do you employ to minimize web bundle sizes, eliminate unused CSS, and optimize Core Web Vitals (LCP, FID, CLS)?",
    ],
    "css": [
        "You mentioned CSS and styling. When do you choose CSS Grid versus Flexbox, and how do you organize scalable styles (e.g., BEM, CSS Modules, Tailwind)?",
    ],

    # ── Backend & Languages ──
    "python": [
        "Since you mentioned Python, how do you handle concurrency or CPU-bound tasks given Python's Global Interpreter Lock (GIL)?",
        "In Python, how do you leverage generators or list comprehensions to optimize memory consumption when processing large datasets?",
        "How do you structure exception handling, custom error classes, and logging in Python backend services to ensure observability in production?",
        "What is your approach to writing modular, PEP 8 compliant, and unit-tested code in Python using pytest?",
    ],
    "node": [
        "You touched on Node.js. How do you handle asynchronous operations, event emitters, and stream processing for large files without exhausting RAM?",
        "In Node.js, how do you structure your backend architecture (controllers, services, repositories) to decouple business logic from framework routes?",
        "How do you implement rate-limiting, request validation, and graceful server shutdowns in a production Node.js/Express service?",
    ],
    "django": [
        "You mentioned Django. How do you optimize Django ORM queries to prevent the N+1 query problem, and how do you handle database migrations safely?",
    ],
    "flask": [
        "You mentioned Flask. How do you organize application factories, blueprints, and database session lifecycles in scalable Flask backends?",
    ],
    "java": [
        "You discussed Java. How does the JVM manage memory across Young and Old generations, and what garbage collection flags or strategies have you explored?",
        "In Java, how do dependency injection and inversion of control (such as in Spring Boot) simplify testing and decoupling of enterprise services?",
    ],
    "c++": [
        "You mentioned C++. How do modern C++ smart pointers (unique_ptr, shared_ptr) enforce RAII and eliminate manual memory leaks?",
    ],

    # ── Databases & Storage ──
    "sql": [
        "You highlighted relational databases and SQL. How would you analyze an EXPLAIN query plan to diagnose and fix a slow query bottleneck in production?",
        "Explain how indexing (like B-Tree or Hash indexes) speeds up search queries, and what trade-offs it introduces during write-heavy workloads.",
        "How do ACID properties protect data integrity during concurrent transactions, and what database isolation level do you typically configure?",
        "How do you approach database schema migrations in a live production environment without causing downtime or table locks?",
    ],
    "database": [
        "Following up on database design: how do you determine when a relational database (like PostgreSQL) is preferable versus a NoSQL store (like MongoDB)?",
        "How do you handle database connection pooling, query timeouts, and failover replicas in high-availability backend architectures?",
    ],
    "mongodb": [
        "You mentioned MongoDB/NoSQL. How do you design document schemas to balance embedding versus referencing, especially for high-cardinality relationships?",
    ],
    "redis": [
        "You discussed Redis. What caching strategies (such as Cache-Aside or Write-Through) and TTL eviction policies do you configure to prevent stale data?",
    ],

    # ── APIs & Architecture ──
    "api": [
        "Following up on your API discussion: what HTTP status codes and payload conventions do you use to communicate client errors and validation issues clearly?",
        "How do you design a RESTful API to be idempotent, especially for payment, checkout, or billing endpoints?",
        "When designing public or microservice APIs, how do you handle authentication, authorization, and token refreshing using JWT or OAuth2?",
        "How do you manage API versioning (e.g., URL path vs header) while maintaining backwards compatibility for existing mobile or web clients?",
    ],
    "microservices": [
        "You touched on microservices. How do you handle distributed tracing, service discovery, and data consistency across independent services?",
        "What patterns (such as circuit breakers, retries with exponential backoff, or dead-letter queues) do you implement to handle cascading service failures?",
    ],

    # ── Cloud, DevOps & Tools ──
    "docker": [
        "You mentioned Docker and containers. How do multi-stage Docker builds help minimize container image size and enhance security in production?",
        "How do you manage environment variables, configuration secrets, and container networking between microservices?",
    ],
    "kubernetes": [
        "You discussed Kubernetes. How do readiness and liveness probes work, and how does the cluster auto-scaler handle sudden traffic spikes?",
    ],
    "git": [
        "You touched on Git. What branching strategy (e.g. GitFlow, Trunk-Based) do you prefer when collaborating, and how do you safely resolve complex merge conflicts?",
        "What is the operational difference between 'git merge' and 'git rebase', and in what circumstances would you avoid rebasing shared branches?",
    ],
    "aws": [
        "You mentioned AWS/cloud. How do you design architectures to be fault-tolerant across multiple Availability Zones with automated load balancing?",
    ],
    "ci/cd": [
        "You discussed CI/CD pipelines. What automated checks (linting, security scanning, unit tests) do you gate before allowing code to deploy to staging or production?",
    ],
    "security": [
        "You touched on security. How do you protect web applications from common vulnerabilities like SQL injection, Cross-Site Scripting (XSS), and CSRF?",
        "How do you store and handle sensitive credentials, API keys, and passwords securely in backend codebases?",
    ],

    # ── Computer Science Core ──
    "oop": [
        "Building on your explanation of Object-Oriented Programming: how do you balance inheritance with composition, and can you share an example where composition proved superior?",
        "Can you illustrate the Single Responsibility Principle or Open/Closed Principle from SOLID with an example from software you have written?",
    ],
    "algorithm": [
        "You discussed algorithms and data structures. How do you evaluate time and space complexity trade-offs when selecting an algorithmic approach for large inputs?",
        "In what practical software engineering scenario would you choose a graph or tree representation over a simple hash map or list?",
    ],
    "testing": [
        "You mentioned testing. What ratio do you maintain between unit tests, integration tests, and end-to-end tests, and how do you mock third-party dependencies?",
    ],

    # ── Project, Experience & Soft Skills ──
    "project": [
        "In the project you just described, what was the single biggest technical hurdle or unexpected bug you encountered, and how did you diagnose and overcome it?",
        "If you were tasked with redesigning that project from scratch today, what architectural decisions or technology choices would you make differently?",
        "What trade-offs did you make in that project between rapid feature delivery and writing long-term scalable, clean code?",
        "If that project scaled to handle 100,000 active concurrent users tomorrow, what part of your system would fail first and how would you redesign it?",
    ],
    "team": [
        "You mentioned collaborating in a team. Can you describe a specific time you had a strong technical disagreement with a colleague, and how you reached a consensus?",
        "How do you deliver constructive, actionable feedback during code reviews without discouraging fellow engineers?",
        "Tell me about a time you mentored or helped a struggling teammate understand a complex concept.",
    ],
    "deadline": [
        "You touched on managing deadlines. If you realized midway through a sprint that a feature could not be delivered on time, how would you renegotiate priorities with leadership?",
        "When multiple urgent bugs and deliverables collide simultaneously, what framework do you use to prioritize what to tackle first?",
    ],
    "failure": [
        "Thank you for sharing that candid experience. Looking back, what safeguards, tests, or processes did you put in place to ensure that mistake never happens again?",
    ],
    "learning": [
        "You emphasized continuous learning. When you need to master a completely new framework or paradigm under tight time constraints, what is your learning methodology?",
    ],
}

FOLLOWUP_TEMPLATES = [
    "Can you elaborate more on {topic}?",
    "That's interesting. How would you handle it differently if {scenario}?",
    "What challenges did you face with {topic} and how did you overcome them?",
    "Can you give a specific example related to {topic}?",
    "How does {topic} apply in a real-world scenario?",
    "What would you do if {topic} didn't work as expected?",
    "How would you explain {topic} to someone with no technical background?",
    "What are the trade-offs involved in {topic}?",
]


# ═══════════════════════════════════════════════════════════
#  PUBLIC AI FUNCTIONS
# ═══════════════════════════════════════════════════════════

def generate_initial_question(interview_type, difficulty, skills='', career_goal='', exclude_questions=None):
    """Generate or select the first question for the interview, avoiding recently asked questions."""
    exclude = set(exclude_questions or [])
    itype = (interview_type or 'general').lower()
    diff = (difficulty or 'medium').lower()

    if genai:
        try:
            return _gemini_generate_initial_question(itype, diff, skills, career_goal, exclude)
        except Exception as e:
            print(f"[AI Engine] Gemini initial question failed: {e}. Using fallback.")

    return _fallback_generate_initial_question(itype, diff, skills, career_goal, exclude)


def generate_adaptive_question(prev_question, prev_answer, evaluation=None, interview_type='general', difficulty='medium', skills='', career_goal='', next_q_num=2, total_questions=5, history=None):
    """
    Dynamically generate Question 2+ based on the candidate's previous answer,
    evaluating their technical terms, concepts, projects, and score to formulate
    a natural, probing, conversational follow-on question.
    """
    itype = (interview_type or 'general').lower()
    diff = (difficulty or 'medium').lower()

    if genai:
        try:
            return _gemini_generate_adaptive_question(
                prev_question, prev_answer, evaluation, itype, diff,
                skills, career_goal, next_q_num, total_questions, history
            )
        except Exception as e:
            print(f"[AI Engine] Gemini adaptive question failed: {e}. Using fallback.")

    return _fallback_generate_adaptive_question(
        prev_question, prev_answer, evaluation, itype, diff,
        skills, career_goal, next_q_num, total_questions, history
    )


def generate_questions(interview_type, difficulty, count, skills='', career_goal=''):
    """Generate multiple interview questions (maintained for backward compatibility)."""
    interview_type = (interview_type or 'general').lower()
    difficulty = (difficulty or 'medium').lower()

    if genai:
        try:
            return _gemini_generate_questions(interview_type, difficulty, count, skills, career_goal)
        except Exception as e:
            print(f"[AI Engine] Gemini question gen failed: {e}. Using fallback.")

    return _fallback_generate_questions(interview_type, difficulty, count)


def evaluate_answer(question, answer, interview_type, difficulty='medium'):
    """Evaluate a student's answer using Gemini API or fallback."""
    if not answer or not answer.strip():
        return {
            'score': 0,
            'technical_knowledge': 0,
            'communication': 0,
            'confidence': 0,
            'relevance': 0,
            'clarity': 0,
            'problem_solving': 0,
            'status': 'Not Good / Mismatched Answer',
            'feedback': 'No answer was provided. Please try to answer the question to the best of your ability.',
            'perfect_answer': _get_perfect_answer(question),
            'improvement': 'Attempt to answer the question even if you are unsure. Partial answers are better than no answer.',
        }

    if genai:
        try:
            return _gemini_evaluate_answer(question, answer, interview_type, difficulty)
        except Exception as e:
            print(f"[AI Engine] Gemini eval failed: {e}. Using fallback.")

    return _fallback_evaluate_answer(question, answer, interview_type)


def generate_followup(question, answer, interview_type):
    """Generate a follow-up question based on the previous answer."""
    if not answer or not answer.strip():
        return None

    if genai:
        try:
            return _gemini_generate_followup(question, answer, interview_type)
        except Exception as e:
            print(f"[AI Engine] Gemini followup failed: {e}. Using fallback.")

    return _fallback_generate_followup(question, answer)


def generate_final_feedback(questions_data, interview_type, difficulty):
    """Generate comprehensive final feedback for the interview session."""
    if genai:
        try:
            return _gemini_final_feedback(questions_data, interview_type, difficulty)
        except Exception as e:
            print(f"[AI Engine] Gemini final feedback failed: {e}. Using fallback.")

    return _fallback_final_feedback(questions_data, interview_type)


# ═══════════════════════════════════════════════════════════
#  GEMINI API IMPLEMENTATIONS
# ═══════════════════════════════════════════════════════════

def _get_gemini_model():
    return genai.GenerativeModel('gemini-1.5-flash')


def _gemini_generate_initial_question(interview_type, difficulty, skills, career_goal, exclude_questions):
    model = _get_gemini_model()
    exclude_list = list(exclude_questions)[:20] if exclude_questions else []
    exclude_text = "\n- ".join(exclude_list) if exclude_list else "None"

    prompt = f"""You are an expert interviewer conducting a {interview_type} interview at {difficulty} difficulty level.
Candidate Profile:
- Skills: {skills if skills else 'General software engineering skills'}
- Career Goal: {career_goal if career_goal else 'Software Developer'}

Generate exactly ONE compelling, professional opening question to start the interview.
Do NOT repeat any of these previously asked questions:
- {exclude_text}

Rules:
- Match the interview type and difficulty level appropriately.
- For technical/coding, ask a strong foundation or technical background question.
- For HR/general, ask a professional introduction or situational question.
- Return ONLY the question text as a single string. No quotes, no markdown, no preamble."""

    response = model.generate_content(prompt)
    text = response.text.strip().strip('"').strip("'")
    if text and len(text) > 10:
        return text
    return _fallback_generate_initial_question(interview_type, difficulty, skills, career_goal, exclude_questions)


def _gemini_generate_adaptive_question(prev_question, prev_answer, evaluation, interview_type, difficulty, skills, career_goal, next_q_num, total_questions, history):
    model = _get_gemini_model()
    score = evaluation.get('score', 5) if isinstance(evaluation, dict) else 5
    feedback = evaluation.get('feedback', '') if isinstance(evaluation, dict) else ''

    # Compile already asked questions to avoid any duplication
    asked = []
    if history:
        for item in history:
            q_txt = item.get('question_text') or item.get('text')
            if q_txt:
                asked.append(q_txt)
    if prev_question and prev_question not in asked:
        asked.append(prev_question)
    asked_str = "\n- ".join(asked) if asked else "None"

    prompt = f"""You are an expert interviewer conducting a live, interactive {interview_type} interview at {difficulty} difficulty level.
Candidate Profile:
- Skills: {skills if skills else 'General technical skills'}
- Target Role: {career_goal if career_goal else 'Software Developer'}

CONVERSATION SO FAR:
Previous Question (#{next_q_num - 1}): "{prev_question}"
Candidate's Verbatim Answer: "{prev_answer}"
Evaluation Score: {score}/10
Evaluator Notes: {feedback}

TASK:
You listened carefully to the candidate's answer. Formulate Question #{next_q_num} of {total_questions} that DIRECTLY BUILDS UPON what the candidate said in their answer.

RULES:
1. ADAPTIVE CONVERSATION: Speak like an active human interviewer (e.g. "You mentioned building X using Y. How did you handle Z...?", "In your answer about A, you pointed out B. What trade-offs did you consider...?").
2. DIG DEEPER:
   - If the candidate mentioned specific technologies, frameworks, projects, or architectural choices (e.g. React, Node, Python, SQL, Docker, AWS), probe into design decisions, edge cases, error handling, or performance in that technology.
   - If they gave an incomplete or weak answer, ask a clarifying follow-up to give them a chance to demonstrate understanding.
   - If they gave a strong answer, elevate the challenge to scale, concurrency, or trade-offs.
3. Keep the tone professional, direct, and conversational.
4. DO NOT repeat any of these previously asked questions:
- {asked_str}

Return ONLY the single question text. No preamble, no quotes, no markdown."""

    response = model.generate_content(prompt)
    text = response.text.strip().strip('"').strip("'")
    if text and len(text) > 10:
        return text
    return _fallback_generate_adaptive_question(prev_question, prev_answer, evaluation, interview_type, difficulty, skills, career_goal, next_q_num, total_questions, history)


def _gemini_generate_questions(interview_type, difficulty, count, skills, career_goal):
    model = _get_gemini_model()
    prompt = f"""You are an expert interviewer. Generate exactly {count} interview questions for a {interview_type} interview at {difficulty} difficulty level.

Student skills: {skills if skills else 'General'}
Career goal: {career_goal if career_goal else 'Software Developer'}

Rules:
- Questions should be realistic, diverse, and professional
- Match the difficulty level appropriately
- Return ONLY a JSON array of strings, each string being one question. No other text.
Example: ["Question 1?", "Question 2?"]"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    match = re.search(r'\\[.*\\]', text, re.DOTALL)
    if match:
        questions = json.loads(match.group())
        return questions[:count]
    return _fallback_generate_questions(interview_type, difficulty, count)


def _gemini_evaluate_answer(question, answer, interview_type, difficulty):
    model = _get_gemini_model()
    prompt = f"""You are an expert interview evaluator with deep semantic understanding. Evaluate this interview answer.

Interview Type: {interview_type}
Difficulty: {difficulty}
Question: {question}
Candidate's Answer: {answer}

EVALUATION RULES:
1. Identify the main intent and expected concepts of the question.
2. Analyze the candidate's answer SEMANTICALLY — do NOT just match keywords.
3. If the answer is relevant and correct, award an appropriate score.
4. If the answer is partially correct, award partial points.
5. If the answer is COMPLETELY UNRELATED, does not address the question, or is a mismatched answer, give 0 points.
6. Do NOT give points simply because the candidate used some keywords from the question.
7. Accept different wording when the candidate communicates the correct concept.
8. Ignore minor grammar, spelling, or sentence-structure mistakes when the meaning is correct.

SCORING (0-10 scale):
- 9-10: Excellent / highly accurate
- 7-8: Good / mostly accurate
- 5-6: Partially correct
- 3-4: Weak / significant missing information
- 1-2: Very poor / minimal relevance
- 0: Incorrect or completely mismatched answer

Also evaluate these sub-categories on the same 0-10 scale:
- technical_knowledge
- communication
- confidence
- relevance
- clarity
- problem_solving

Return ONLY valid JSON in this exact format:
{{"score": 8, "technical_knowledge": 7, "communication": 8, "confidence": 7, "relevance": 9, "clarity": 8, "problem_solving": 7, "status": "Good", "feedback": "Brief explanation of why this score was given", "perfect_answer": "The ideal complete answer to this question", "improvement": "What the candidate should have included or improved"}}

STATUS must be exactly one of: "Excellent", "Good", "Average / Partially Correct", "Needs Improvement", "Not Good / Mismatched Answer"

If the answer is mismatched/unrelated:
- Set score and all sub-scores to 0
- Set status to "Not Good / Mismatched Answer"
- Set feedback to "Your answer does not address the question being asked."
- Still provide a perfect_answer and improvement"""

    response = model.generate_content(prompt)
    text = response.text.strip()
    match = re.search(r'\\{.*\\}', text, re.DOTALL)
    if match:
        result = json.loads(match.group())
        for key in ['score', 'technical_knowledge', 'communication', 'confidence', 'relevance', 'clarity', 'problem_solving']:
            if key not in result:
                result[key] = 5
        if 'feedback' not in result:
            result['feedback'] = 'Good attempt.'
        if 'status' not in result:
            result['status'] = _get_status_from_score(result['score'])
        if 'perfect_answer' not in result:
            result['perfect_answer'] = ''
        if 'improvement' not in result:
            result['improvement'] = ''
        return result
    return _fallback_evaluate_answer(question, answer, interview_type)


def _gemini_generate_followup(question, answer, interview_type):
    model = _get_gemini_model()
    prompt = f"""You are an expert interviewer conducting a {interview_type} interview.
The candidate just answered a question. Generate ONE natural follow-up question based on their answer.

Original Question: {question}
Candidate's Answer: {answer}

The follow-up should:
- Dig deeper into something the candidate mentioned
- Be relevant to the interview type
- Feel natural and conversational

Return ONLY the follow-up question as a single string. No quotes, no extra text."""

    response = model.generate_content(prompt)
    followup = response.text.strip().strip('"').strip("'")
    if followup and len(followup) > 10:
        return followup
    return _fallback_generate_followup(question, answer)


def _gemini_final_feedback(questions_data, interview_type, difficulty):
    model = _get_gemini_model()

    qa_text = ""
    for i, q in enumerate(questions_data, 1):
        raw_sc = q.get('score', 0)
        norm_sc = raw_sc * 10 if raw_sc <= 10 else raw_sc
        qa_text += f"\\nQ{i}: {q.get('question_text', '')}\\nA{i}: {q.get('answer_text', 'No answer')}\\nScore: {round(norm_sc, 1)}/100 ({round(raw_sc if raw_sc <= 10 else raw_sc / 10, 1)}/10)\\n"

    prompt = f"""You are an expert career counselor evaluating a student's {interview_type} interview performance at {difficulty} difficulty.

Here are the questions, answers, and scores:
{qa_text}

Provide a comprehensive evaluation in this exact JSON format:
{{
    "feedback_summary": "2-3 paragraph overall assessment",
    "strengths": ["strength 1", "strength 2", "strength 3"],
    "weaknesses": ["weakness 1", "weakness 2"],
    "improvements": ["improvement area 1", "improvement area 2", "improvement area 3"],
    "recommendations": ["topic/resource to study 1", "topic/resource 2", "topic/resource 3"],
    "readiness_pct": 65
}}

Be constructive, specific, and encouraging. The readiness_pct should be 0-100.
Return ONLY valid JSON."""

    response = model.generate_content(prompt)
    text = response.text.strip()
    match = re.search(r'\\{.*\\}', text, re.DOTALL)
    if match:
        return json.loads(match.group())
    return _fallback_final_feedback(questions_data, interview_type)


def _get_status_from_score(score):
    if score >= 9:
        return "Excellent"
    elif score >= 7:
        return "Good"
    elif score >= 5:
        return "Average / Partially Correct"
    elif score >= 1:
        return "Needs Improvement"
    else:
        return "Not Good / Mismatched Answer"


# ═══════════════════════════════════════════════════════════
#  FALLBACK QUESTION GENERATORS
# ═══════════════════════════════════════════════════════════

def _fallback_generate_initial_question(interview_type, difficulty, skills, career_goal, exclude_questions):
    """Select a personalized initial opening question that hasn't been recently asked."""
    itype = interview_type.lower()
    diff = difficulty.lower()
    if itype not in QUESTION_BANK:
        itype = 'general'
    if diff not in QUESTION_BANK[itype]:
        diff = 'medium'

    pool = list(QUESTION_BANK[itype][diff])
    
    # Check if candidate skills match any questions
    skills_lower = (skills or '').lower()
    goal_lower = (career_goal or '').lower()
    user_context = f"{skills_lower} {goal_lower}"
    
    # Filter out excluded questions
    available = [q for q in pool if q not in exclude_questions]
    if not available:
        # If all in current difficulty are excluded, check other difficulties
        for other_diff, other_qs in QUESTION_BANK[itype].items():
            for q in other_qs:
                if q not in exclude_questions and q not in available:
                    available.append(q)

    # Fallback to pool if still empty
    if not available:
        available = pool

    # Prioritize questions matching skills/career goal
    scored_qs = []
    for q in available:
        score = 0
        words = q.lower().split()
        for w in words:
            if len(w) > 3 and w in user_context:
                score += 1
        scored_qs.append((score, q))

    scored_qs.sort(key=lambda x: x[0], reverse=True)
    best_matches = [q for score, q in scored_qs if score == scored_qs[0][0]]
    return random.choice(best_matches if best_matches else available)


def _fallback_generate_adaptive_question(prev_question, prev_answer, evaluation, interview_type, difficulty, skills, career_goal, next_q_num, total_questions, history):
    """
    Intelligent NLP & context-driven adaptive question generation based on what
    the student said in their previous answer.
    """
    answer_text = (prev_answer or '').strip()
    ans_lower = answer_text.lower()
    words = re.findall(r'\\b[a-zA-Z0-9_#+\\.-]+\\b', ans_lower)
    score = evaluation.get('score', 5) if isinstance(evaluation, dict) else 5

    # Gather already asked questions to prevent any repetition
    asked = set()
    if history:
        for item in history:
            q_txt = item.get('question_text') or item.get('text')
            if q_txt:
                asked.add(q_txt)
    if prev_question:
        asked.add(prev_question)

    # Detect technologies, concepts, and themes mentioned in the student's answer
    detected_topics = []
    for topic, qlist in ADAPTIVE_TOPIC_QUESTIONS.items():
        # Match topic as whole word
        pattern = r'\\b' + re.escape(topic) + r'\\b'
        if re.search(pattern, ans_lower):
            detected_topics.append(topic)

    # Detect project phrases ("i built", "we developed", "my project", "in my app", etc.)
    project_indicators = ["i built", "we built", "i developed", "we developed", "my project", "in my project", "i worked on", "i implemented", "we created"]
    has_project_mention = any(pi in ans_lower for pi in project_indicators)
    if has_project_mention and "project" not in detected_topics:
        detected_topics.append("project")

    # If topics were detected, select an appropriate question
    candidate_questions = []
    for topic in detected_topics:
        for q in ADAPTIVE_TOPIC_QUESTIONS.get(topic, []):
            if q not in asked:
                candidate_questions.append(q)

    if candidate_questions:
        # If score is high (8-10), pick questions containing 'optimize', 'trade-offs', 'scale', 'bottleneck'
        if score >= 8:
            advanced = [q for q in candidate_questions if any(w in q.lower() for w in ['scale', 'trade-off', 'optimize', 'concurrency', 'bottleneck', 'internal'])]
            if advanced:
                return random.choice(advanced)
        return random.choice(candidate_questions)

    # If answer was brief or low-scoring (score <= 4 or fewer than 15 words)
    if score <= 4 or len(words) < 15:
        # Extract the core topic of the previous question
        prev_words = [w for w in prev_question.replace('?', '').split() if len(w) > 4 and w.lower() not in ['difference', 'between', 'explain', 'describe', 'preferred', 'approach', 'would']]
        focus_word = prev_words[0] if prev_words else "that concept"
        clarifications = [
            f"In your previous response, you touched briefly on {focus_word}. Could you walk me through a concrete, step-by-step example of how this works in a production scenario?",
            f"Let's explore that topic a bit deeper: what are the primary advantages and potential failure modes of this approach?",
            f"If you were explaining {focus_word} to a junior engineer who had never seen it before, what fundamental principles would you emphasize?",
            f"Can you give an example of a time you applied or observed {focus_word} in an actual software project or coursework?",
        ]
        available_clarifications = [q for q in clarifications if q not in asked]
        if available_clarifications:
            return random.choice(available_clarifications)

    # Fallback: Extract meaningful nouns / phrases from the candidate's answer
    stop_words = {
        'the', 'and', 'for', 'that', 'this', 'with', 'from', 'have', 'were', 'been',
        'what', 'when', 'where', 'which', 'will', 'would', 'could', 'should', 'about',
        'also', 'into', 'some', 'more', 'than', 'like', 'then', 'them', 'their', 'they',
        'because', 'used', 'using', 'very', 'just', 'well', 'good', 'make', 'made'
    }
    substantive_words = [w for w in words if len(w) > 4 and w not in stop_words]
    if substantive_words:
        top_concept = substantive_words[0]
        contextual_syntheses = [
            f"You mentioned '{top_concept}' in your response. How did that specifically impact your overall solution, and what alternatives did you weigh against it?",
            f"Following up on your points regarding '{top_concept}': how do you verify and test this to guarantee reliability when traffic or data volume surges?",
            f"That's a key observation about '{top_concept}'. Can you describe a scenario where that approach encountered unexpected edge cases, and how you addressed them?",
            f"Building on what you shared about '{top_concept}': what are the key trade-offs between speed of execution and system maintainability in that context?",
        ]
        available_syntheses = [q for q in contextual_syntheses if q not in asked]
        if available_syntheses:
            return random.choice(available_syntheses)

    # General fallback to a fresh question from the question bank that hasn't been asked
    itype = interview_type.lower() if interview_type in QUESTION_BANK else 'general'
    diff = difficulty.lower() if difficulty in QUESTION_BANK[itype] else 'medium'
    fresh_pool = [q for q in QUESTION_BANK[itype][diff] if q not in asked]
    if not fresh_pool:
        fresh_pool = [q for qs in QUESTION_BANK[itype].values() for q in qs if q not in asked]
    if fresh_pool:
        return random.choice(fresh_pool)

    return f"Building on your last answer, can you elaborate on the technical challenges and trade-offs you encountered?"


def _fallback_generate_questions(interview_type, difficulty, count):
    """Select random non-repeating questions from the expanded built-in bank."""
    itype = interview_type.lower()
    diff = difficulty.lower()
    if itype not in QUESTION_BANK:
        itype = 'general'
    if diff not in QUESTION_BANK[itype]:
        diff = 'medium'

    pool = list(QUESTION_BANK[itype][diff])
    if count > len(pool):
        for other_diff, other_qs in QUESTION_BANK[itype].items():
            if other_diff != diff:
                for q in other_qs:
                    if q not in pool:
                        pool.append(q)
    if count > len(pool) and itype != 'general':
        for other_diff, other_qs in QUESTION_BANK.get('general', {}).items():
            for q in other_qs:
                if q not in pool:
                    pool.append(q)

    count = min(count, len(pool))
    return random.sample(pool, count)


# ═══════════════════════════════════════════════════════════
#  EVALUATION ENGINE & PERFECT ANSWERS
# ═══════════════════════════════════════════════════════════
'''

print('Base code length:', len(code))
'''
