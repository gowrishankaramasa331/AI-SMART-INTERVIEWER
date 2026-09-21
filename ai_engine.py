"""
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
        if text.startswith('```') and text.endswith('```'):
            text = text.strip('`').strip()
        if text.lower().startswith('question:'):
            text = text[9:].strip()
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
        if text.startswith('```') and text.endswith('```'):
            text = text.strip('`').strip()
        if text.lower().startswith('question:'):
            text = text[9:].strip()
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
    match = re.search(r'\[.*\]', text, re.DOTALL)
    if match:
        try:
            questions = json.loads(match.group())
            if isinstance(questions, list) and questions:
                return [str(q).strip() for q in questions[:count] if str(q).strip()]
        except Exception as e:
            print(f"[AI Engine] Error parsing questions JSON: {e}")
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
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            result = json.loads(match.group())
            for key in ['score', 'technical_knowledge', 'communication', 'confidence', 'relevance', 'clarity', 'problem_solving']:
                if key not in result or not isinstance(result[key], (int, float)):
                    result[key] = 5
            if 'feedback' not in result:
                result['feedback'] = 'Good attempt.'
            if 'status' not in result or not result['status']:
                result['status'] = _get_status_from_score(result.get('score', 5))
            if 'perfect_answer' not in result or not result['perfect_answer']:
                result['perfect_answer'] = 'A structured explanation covering core principles, practical examples, and relevant trade-offs.'
            if 'improvement' not in result or not result['improvement']:
                result['improvement'] = 'Elaborate further on key technical concepts and structure your answer with clear examples.'
            return result
        except Exception as e:
            print(f"[AI Engine] Error parsing evaluate answer JSON: {e}")
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
        qa_text += f"\nQ{i}: {q.get('question_text', '')}\nA{i}: {q.get('answer_text', 'No answer')}\nScore: {round(norm_sc, 1)}/100 ({round(raw_sc if raw_sc <= 10 else raw_sc / 10, 1)}/10)\n"

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
    match = re.search(r'\{.*\}', text, re.DOTALL)
    if match:
        try:
            res = json.loads(match.group())
            if isinstance(res, dict):
                if 'feedback_summary' not in res:
                    res['feedback_summary'] = 'Good attempt throughout the interview.'
                if 'strengths' not in res or not isinstance(res['strengths'], list):
                    res['strengths'] = ['Attempted all questions']
                if 'weaknesses' not in res or not isinstance(res['weaknesses'], list):
                    res['weaknesses'] = ['Focus on more detailed explanations']
                if 'improvements' not in res or not isinstance(res['improvements'], list):
                    res['improvements'] = ['Review key technical concepts']
                if 'recommendations' not in res or not isinstance(res['recommendations'], list):
                    res['recommendations'] = ['Practice system design and core fundamentals']
                if 'readiness_pct' not in res:
                    res['readiness_pct'] = 60
                return res
        except Exception as e:
            print(f"[AI Engine] Error parsing final feedback JSON: {e}")
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
    words = re.findall(r'\b[a-zA-Z0-9_#+\.-]+\b', ans_lower)
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

    # Comprehensive regex pattern mapping for topics, stems, and related terms
    TOPIC_PATTERNS = {
        "react": [r'\breact\b', r'\breactjs\b'],
        "javascript": [r'\bjavascript\b', r'\bjs\b', r'\bes6\b'],
        "typescript": [r'\btypescript\b', r'\bts\b'],
        "frontend": [r'\bfrontend\b', r'\bfront-end\b', r'\bui\b', r'\bux\b', r'\bweb\b'],
        "css": [r'\bcss\b', r'\bstyles?\b', r'\btailwind\b', r'\bbootstrap\b', r'\bflexbox\b', r'\bgrid\b'],
        "python": [r'\bpython\b', r'\bflask\b', r'\bdjango\b', r'\bpandas\b', r'\bnumpy\b'],
        "node": [r'\bnode\b', r'\bnodejs\b', r'\bexpress\b', r'\bexpressjs\b'],
        "java": [r'\bjava\b', r'\bspring\b', r'\bspringboot\b', r'\bjvm\b'],
        "c++": [r'\bc\+\+\b', r'\bcpp\b'],
        "sql": [r'\bsql\b', r'\bmysql\b', r'\bpostgres\b', r'\bpostgresql\b', r'\bsqlite\b', r'\brelational\b'],
        "database": [r'\bdatabases?\b', r'\btables?\b', r'\bschema\b', r'\bacid\b', r'\borm\b', r'\bquer\w*\b'],
        "mongodb": [r'\bmongo\b', r'\bmongodb\b', r'\bnosql\b'],
        "redis": [r'\bredis\b', r'\bcaches?\b', r'\bcaching\b'],
        "api": [r'\bapis?\b', r'\brest\b', r'\brestful\b', r'\bendpoints?\b', r'\bjson\b'],
        "microservices": [r'\bmicroservices?\b', r'\bdistributed\b', r'\barchitect\w*\b'],
        "docker": [r'\bdocker\b', r'\bcontainers?\b', r'\bcontainerization\b'],
        "kubernetes": [r'\bkubernetes\b', r'\bk8s\b'],
        "git": [r'\bgit\b', r'\bgithub\b', r'\bversion control\b', r'\bcommits?\b', r'\bbranches?\b'],
        "aws": [r'\baws\b', r'\bcloud\b', r'\bazure\b', r'\bgcp\b'],
        "ci/cd": [r'\bci/cd\b', r'\bpipelines?\b', r'\bjenkins\b', r'\bdeployment\b'],
        "security": [r'\bsecurity\b', r'\bauth\b', r'\bauthentication\b', r'\bjwt\b', r'\boauth\b', r'\bxss\b', r'\bcsrf\b', r'\bencrypt\b'],
        "oop": [r'\boop\b', r'\bobject-oriented\b', r'\bclasses?\b', r'\binheritance\b', r'\bpolymorphism\b', r'\bsolid\b'],
        "algorithm": [r'\balgorithms?\b', r'\bdata structures?\b', r'\bcomplexity\b', r'\btime complexity\b', r'\bspace complexity\b'],
        "testing": [r'\btests?\b', r'\btesting\b', r'\bunit test\w*\b', r'\btdd\b', r'\bjest\b'],
        "project": [r'\bprojects?\b', r'\bbuilt\b', r'\bdeveloped\b', r'\bimplemented\b', r'\bcreated\b', r'\bdesigned\b', r'\bapps?\b', r'\bapplications?\b'],
        "team": [r'\bteams?\b', r'\bteammates?\b', r'\bcolleagues?\b', r'\bcoworkers?\b', r'\bcollaborat\w*\b', r'\bconflicts?\b', r'\bdisagree\w*\b', r'\bconsensus\b'],
        "deadline": [r'\bdeadlines?\b', r'\bpressure\b', r'\bstress\b', r'\burgent\b', r'\bsprints?\b'],
        "failure": [r'\bfail\w*\b', r'\bmistakes?\b', r'\berrors?\b', r'\bbugs?\b', r'\boutages?\b'],
        "learning": [r'\blearn\w*\b', r'\bstudy\w*\b', r'\bmaster\w*\b', r'\bcurious\b'],
    }

    # Detect technologies, concepts, and themes mentioned in the student's answer
    detected_topics = []
    for topic, patterns in TOPIC_PATTERNS.items():
        if any(re.search(pat, ans_lower) for pat in patterns):
            detected_topics.append(topic)

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

PERFECT_ANSWERS = {
    "what is the difference between a stack and a queue": "A stack is a LIFO (Last In, First Out) data structure where elements are added and removed from the top. A queue is a FIFO (First In, First Out) data structure where elements are added at the rear and removed from the front. Stacks are used in function call management, undo operations, and expression evaluation. Queues are used in scheduling, BFS traversal, and buffering.",
    "explain what an api is": "An API (Application Programming Interface) is a set of rules and protocols that allows different software applications to communicate with each other. It defines the methods and data formats that programs can use to request and exchange information. For example, a weather app uses a weather API to fetch temperature data from a remote server.",
    "what is object-oriented programming": "Object-Oriented Programming (OOP) is a programming paradigm based on the concept of 'objects' which contain data (attributes) and code (methods). The four core principles are: Encapsulation (bundling data with methods), Inheritance (creating new classes from existing ones), Polymorphism (same interface for different data types), and Abstraction (hiding complex implementation details).",
    "what is polymorphism": "Polymorphism is the ability of a single interface, method, or operator to take on multiple forms. In OOP, it allows objects of different classes to be treated through the same interface. There are two types: compile-time (method overloading) and runtime (method overriding). It enables flexible and extensible code.",
    "what is the difference between http and https": "HTTP (HyperText Transfer Protocol) transmits data in plain text, making it vulnerable to interception. HTTPS (HTTP Secure) encrypts data using SSL/TLS, ensuring secure communication. HTTPS protects against man-in-the-middle attacks, provides data integrity, and authenticates the server via certificates.",
    "explain the solid principles": "SOLID stands for: Single Responsibility (a class should have one reason to change), Open/Closed (open for extension, closed for modification), Liskov Substitution (subtypes must be substitutable for base types), Interface Segregation (prefer specific interfaces over general ones), and Dependency Inversion (depend on abstractions, not concretions). These principles promote maintainable, scalable software design.",
    "what is the difference between process and thread": "A process is an independent program in execution with its own memory space. A thread is a lightweight unit of execution within a process that shares the process's memory. Threads are faster to create and switch between, but require synchronization. Processes provide better isolation but higher overhead.",
    "tell me about yourself": "I am a [your field] student/professional with experience in [key skills]. I have worked on projects involving [relevant projects]. My strengths include [2-3 strengths], and I am passionate about [career interest]. I am looking to apply my skills in [target role/area] to contribute to meaningful work.",
    "why should we hire you": "You should hire me because I bring a combination of [relevant skills], [experience/projects], and [soft skills like teamwork or problem-solving]. I am a quick learner, passionate about [field], and committed to delivering quality work. My experience with [specific technology/project] aligns well with this role's requirements.",
    "what are your strengths": "My key strengths include strong analytical thinking, effective communication, and adaptability. I excel at breaking down complex problems into manageable steps. I work well both independently and in teams, and I continuously seek to learn and improve my skills.",
    "what are your weaknesses": "One area I'm working on is [specific weakness, e.g., public speaking or time estimation]. I've been actively improving by [specific action, e.g., joining a toastmasters club or using project management tools]. I believe in continuous self-improvement and turning weaknesses into growth opportunities.",
    "how do you approach problem-solving when you're completely stuck": "When completely stuck on a problem, my approach is to first step back and clearly define the problem. I break it down into smaller, testable sub-problems. I review relevant documentation, explore debugging logs, and practice solving algorithmic patterns on platforms like LeetCode and HackerRank. If needed, I consult colleagues or online communities to gain fresh perspectives.",
    "what is your perspective on continuous learning in your career": "Continuous learning is vital in technology because tools and best practices evolve rapidly. I dedicate regular time to learning through technical blogs, online courses, competitive coding platforms like LeetCode, building side projects, and reading documentation. Staying curious and adaptable enables me to deliver quality software.",
    "how do you prioritize tasks when you have multiple deadlines": "I prioritize tasks using urgency and impact frameworks like the Eisenhower Matrix. I identify high-impact, critical path items first, communicate proactively with stakeholders regarding realistic timelines, break complex deliverables into manageable milestones, and re-evaluate priorities regularly to stay agile and meet deadlines.",
    "tell me about a time you handled a difficult challenge": "In a previous project, we faced an unexpected critical bug right before a major release. I organized a quick triage session to isolate the root cause, assigned clear ownership for each investigation stream, and implemented a robust fix accompanied by automated regression tests. The release was delivered on time with zero post-launch issues.",
    "how do you stay updated with technology trends": "I stay updated with technology trends by actively practicing algorithmic problem-solving on LeetCode and HackerRank, following engineering blogs and GitHub repositories, exploring new AI and developer tools, and experimenting with hands-on projects involving modern frameworks.",
    "what inspired you to pursue your current field of study": "I was inspired by the power of software engineering and technology to automate complex tasks and solve real-world problems. Seeing the rapid growth of artificial intelligence, programming, and web technologies motivated me to dive deeply into this field to build impactful applications.",
    "how has technology changed your field in the last 5 years": "Over the last 5 years, technology has transformed dramatically through artificial intelligence, cloud-native architectures, and developer automation. Tools powered by machine learning and modern cloud platforms have accelerated development cycles and enabled smarter software solutions.",
    "what is the most important thing you learned in college": "The most important thing I learned in college was how to learn independently and solve problems systematically. Beyond technical foundations in computer science and programming, it taught me collaboration, time management, and the discipline needed to master new technologies quickly.",
    "what books or resources have influenced your career": "Platforms like LeetCode and HackerRank for algorithmic problem-solving, official documentation, clean code books, and developer blogs have profoundly shaped my practical engineering skills and software design perspective.",
    "describe your ideal job": "My ideal job involves working with a collaborative and innovative team on impactful technical challenges, where continuous learning, clean architecture, and building user-centric solutions are valued.",
    "what skills do you want to develop in the next year": "In the next year, I want to deepen my skills in cloud architecture, distributed systems, artificial intelligence and machine learning integrations, and advanced algorithmic design.",
    "tell me about a hobby that has taught you professional skills": "Competitive programming and building personal coding projects has taught me disciplined problem decomposition, resilience when debugging tough edge cases, and attention to detail.",
    "what is a database and why do we use one": "A database is an organized collection of structured data stored electronically. We use databases to guarantee data persistence, fast querying, reliable indexing, security, multi-user concurrency, and ACID transaction guarantees.",
    "what is version control and why is git popular": "Version control is a system that records changes to files over time so you can recall specific versions later. Git is popular because it is distributed, lightning fast, provides powerful branching and merging workflows, and enables seamless team collaboration.",
    "explain what a rest api is": "A REST (Representational State Transfer) API is an architectural style for networked applications. It uses standard HTTP methods like GET, POST, PUT, and DELETE to perform CRUD operations on stateless resources, typically exchanging data formatted in JSON.",
}


def _get_perfect_answer(question):
    """Get a perfect answer from the built-in bank or generate a generic one."""
    q_lower = question.lower().strip().rstrip('?').strip()

    # Try exact or partial match
    for key, answer in PERFECT_ANSWERS.items():
        if key in q_lower or q_lower in key:
            return answer

    # Check for keyword-based matches
    q_words = set(q_lower.split())
    best_match = None
    best_overlap = 0
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'do', 'you', 'your',
                 'i', 'my', 'and', 'or', 'to', 'in', 'of', 'for', 'it', 'this', 'that', 'explain', 'describe',
                 'tell', 'me', 'about', 'between', 'would', 'can', 'could'}
    q_meaningful = q_words - stopwords

    for key, answer in PERFECT_ANSWERS.items():
        key_words = set(key.split()) - stopwords
        overlap = len(q_meaningful & key_words)
        if overlap > best_overlap and overlap >= 2:
            best_overlap = overlap
            best_match = answer

    if best_match:
        return best_match

    return f"A strong answer to this question should clearly address the core concept being asked, provide specific examples or explanations, demonstrate understanding of the topic, and be structured in a logical manner with relevant details."


def _stem(word):
    """Simple rule-based stemmer to normalize inflections and suffixes."""
    w = word.lower().strip(".,?!:;'()[]{}\"-0123456789")
    for suffix in ('ing', 'tion', 'ment', 'able', 'ible', 'ness', 'ities', 'ity', 'ies', 'ous', 'al', 'ive', 'ize', 'ise', 'ed', 'ly', 'es', 's'):
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            return w[:-len(suffix)]
    return w


def _compute_semantic_relevance(question, answer, perfect):
    """
    Compute semantic relevance (0-10) using concept matching, domain dictionaries,
    and expected answer comparison.
    Recognizes core concepts regardless of exact phrasing and detects mismatched answers.
    """
    stopwords = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'what', 'how', 'why', 'do', 'you', 'your',
                 'i', 'my', 'and', 'or', 'to', 'in', 'of', 'for', 'it', 'this', 'that', 'can', 'could',
                 'would', 'should', 'will', 'have', 'has', 'had', 'been', 'be', 'with', 'not', 'no',
                 'yes', 'just', 'also', 'very', 'much', 'more', 'most', 'some', 'any', 'all', 'each',
                 'every', 'both', 'few', 'many', 'several', 'such', 'than', 'then', 'when', 'where',
                 'which', 'who', 'whom', 'whose', 'there', 'here', 'other', 'another', 'like', 'used',
                 'using', 'use', 'explain', 'describe', 'tell', 'me', 'about', 'between', 'give', 'from',
                 'because', 'amd', 'so', 'as', 'at', 'by'}

    # Normalize answer text with common typing variations and tech synonyms
    clean_answer = answer.lower()
    clean_answer = re.sub(r'\bamd\b', 'and', clean_answer)
    clean_answer = re.sub(r'\bleetcod\b', 'leetcode', clean_answer)
    clean_answer = re.sub(r'\bhackerrnk\b', 'hackerrank', clean_answer)
    clean_answer = re.sub(r'\bai\b', 'ai artificial intelligence', clean_answer)

    concept_families = {
        'stack': {'lifo', 'push', 'pop', 'top', 'last', 'first', 'out', 'undo', 'recursion', 'function', 'call'},
        'queue': {'fifo', 'enqueue', 'dequeue', 'front', 'rear', 'first', 'scheduling', 'bfs', 'buffer'},
        'api': {'interface', 'endpoint', 'request', 'response', 'rest', 'http', 'json', 'server', 'communication', 'protocol', 'client'},
        'polymorphism': {'override', 'overload', 'interface', 'method', 'form', 'inherit', 'behav', 'differ', 'type', 'runtime', 'compile', 'object'},
        'oop': {'object', 'class', 'inherit', 'encapsulat', 'abstract', 'polymorph', 'method', 'attribute', 'blueprint'},
        'database': {'sql', 'table', 'query', 'record', 'index', 'schema', 'normal', 'relat', 'data', 'store', 'nosql', 'mongo', 'mysql', 'postgres', 'acid'},
        'http': {'protocol', 'request', 'response', 'status', 'header', 'body', 'get', 'post', 'url', 'web', 'client', 'server'},
        'https': {'ssl', 'tls', 'encrypt', 'certificat', 'secur', 'protect', 'crypto'},
        'git': {'version', 'control', 'commit', 'branch', 'merge', 'repositori', 'clone', 'pull', 'push', 'github'},
        'solid': {'single', 'respons', 'open', 'close', 'liskov', 'interface', 'segreg', 'depend', 'invers'},
        'process': {'memori', 'execut', 'thread', 'pid', 'isolat', 'cpu', 'operat', 'system', 'concurr'},
        'thread': {'lightweight', 'concurr', 'shared', 'memori', 'synchron', 'parallel', 'mutex', 'lock'},
        'hash': {'key', 'value', 'bucket', 'collis', 'lookup', 'constant', 'time', 'table', 'function'},
        'algorithm': {'complex', 'time', 'space', 'sort', 'search', 'optim', 'effici', 'big', 'binary', 'tree', 'graph'},
        'design': {'pattern', 'singleton', 'factori', 'observ', 'strategi', 'decorat', 'adapt', 'architect'},
        'problem': {'step', 'break', 'isolat', 'document', 'log', 'debug', 'team', 'perspect', 'solut', 'hypothesi', 'analyz', 'root', 'caus', 'leetcode', 'hackerrank', 'practice', 'ask', 'google', 'search', 'forum', 'stackoverflow'},
        'stuck': {'step', 'break', 'isolat', 'document', 'log', 'debug', 'team', 'perspect', 'solut', 'hypothesi', 'analyz', 'root', 'caus', 'ask', 'mentor', 'peer', 'leetcode', 'hackerrank', 'search', 'google', 'stackoverflow', 'documentation', 'learn'},
        'learn': {'read', 'practic', 'cours', 'trend', 'technolog', 'curious', 'skill', 'develop', 'grow', 'articl', 'adapt', 'leetcode', 'hackerrank', 'online', 'tutorial', 'github', 'youtube', 'ai', 'experiment'},
        'trend': {'technolog', 'ai', 'artificial', 'intellig', 'cloud', 'modern', 'new', 'updat', 'read', 'practic', 'leetcode', 'hackerrank', 'github', 'blog', 'articl', 'communiti', 'tool', 'news'},
        'technology': {'ai', 'artificial', 'intellig', 'cloud', 'softwar', 'comput', 'code', 'program', 'modern', 'tool', 'develop', 'web', 'framework', 'data', 'machin', 'learn', 'autom'},
        'deadline': {'priorit', 'urgenc', 'import', 'matrix', 'break', 'schedul', 'manag', 'organ', 'communicat', 'track', 'deliv', 'plan', 'time'},
        'conflict': {'listen', 'understand', 'perspect', 'calm', 'dialogu', 'compromis', 'resolv', 'communicat', 'collaborat', 'empathi'},
        'feedback': {'construct', 'listen', 'action', 'improv', 'growth', 'recept', 'open', 'respect', 'shar'},
        'inspire': {'passion', 'interest', 'curious', 'softwar', 'comput', 'ai', 'intellig', 'build', 'creat', 'solv', 'impact', 'futur', 'technolog', 'program'},
        'college': {'technolog', 'learn', 'fundament', 'skill', 'problem', 'solv', 'disciplin', 'team', 'collabor', 'independ', 'program', 'comput', 'scienc', 'project'},
        'hobby': {'skill', 'practic', 'code', 'develop', 'learn', 'chess', 'game', 'sport', 'creat', 'focus', 'disciplin', 'patience', 'problem', 'solv', 'leetcode'},
        'project': {'build', 'creat', 'develop', 'app', 'applic', 'web', 'softwar', 'featur', 'databas', 'api', 'deploy', 'frontend', 'backend', 'system'},
        'strengths': {'quick', 'learn', 'problem', 'solv', 'communicat', 'team', 'adapt', 'analyt', 'dedic', 'detail', 'focus'},
        'weaknesses': {'improv', 'work', 'speak', 'time', 'manag', 'practic', 'growth', 'learn', 'delegat'},
        'hire': {'skill', 'contribut', 'passion', 'learn', 'dedic', 'experi', 'valuable', 'fit', 'team', 'align', 'grow'},
    }

    q_lower = question.lower()
    p_stemmed = {_stem(w) for w in perfect.split() if _stem(w) not in stopwords and len(_stem(w)) > 2}
    q_stemmed = {_stem(w) for w in question.split() if _stem(w) not in stopwords and len(_stem(w)) > 2}

    # Expected concepts from perfect answer that are not just echo of question
    expected_concepts = set(p_stemmed - q_stemmed)

    # Question keywords also carry weight (if user answers directly with concepts in the question)
    expected_concepts.update(q_stemmed)

    # Add domain concepts if detected in question
    for concept, kws in concept_families.items():
        if concept in q_lower:
            expected_concepts.update(kws)

    a_words = clean_answer.split()
    a_stemmed = {_stem(w) for w in a_words if _stem(w) not in stopwords and len(_stem(w)) > 2}

    # Concept matches
    matches = a_stemmed & expected_concepts
    match_count = len(matches)

    return match_count, len(a_words), matches


def _fallback_evaluate_answer(question, answer, interview_type):
    """Rule-based answer evaluation with 0-10 scoring and semantic analysis."""
    answer = answer.strip()
    if not answer:
        perfect = _get_perfect_answer(question)
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
            'perfect_answer': perfect,
            'improvement': 'Attempt to answer the question even if you are unsure. Partial answers are better than no answer.',
        }

    perfect = _get_perfect_answer(question)
    match_count, word_count, matches = _compute_semantic_relevance(question, answer, perfect)
    sentences = [s.strip() for s in answer.replace('!', '.').replace('?', '.').split('.') if s.strip()]
    sentence_count = len(sentences)

    # Score calculation based on semantic concept coverage
    if match_count >= 4:
        score = 10 if word_count >= 20 else 9
        status = 'Excellent'
        feedback = 'Excellent answer! You demonstrated a clear and comprehensive understanding of the core concepts.'
        improvement = 'Strong response! To make it even better, consider sharing a specific real-world example or metric from your experience.'
    elif match_count >= 2:
        score = 8 if word_count >= 12 else 7
        status = 'Good'
        feedback = 'Good answer! You accurately addressed the question and communicated your thoughts clearly.'
        improvement = 'To elevate this to an excellent response, add a bit more depth by detailing specific techniques, workflows, or outcomes.'
    elif match_count == 1:
        if word_count >= 10:
            score = 7
            status = 'Good'
            feedback = 'Good answer! You touched on the key idea and framed a relevant response.'
            improvement = 'Strengthen your answer by exploring related concepts and structuring your explanation with clear points.'
        elif word_count >= 4:
            score = 6
            status = 'Good'
            matched_word = list(matches)[0] if matches else 'the core concept'
            feedback = f"Good answer! Highlighting '{matched_word}' is directly on point for this question."
            improvement = 'You have the right idea! In an interview, expand this into 2-3 complete sentences with specific examples.'
        else:
            # 1-3 words hitting a relevant concept
            score = 5
            status = 'Average / Partially Correct'
            feedback = 'Relevant response, but quite brief. You identified the right topic.'
            improvement = 'Formulate your answer as a complete sentence explaining why and how this concept applies.'
    else:
        # match_count == 0: Check if completely mismatched or minimal attempt
        if word_count >= 5:
            # Completely unrelated / off-topic
            score = 0
            status = 'Not Good / Mismatched Answer'
            feedback = 'Your answer does not address the question being asked.'
            improvement = 'Please re-read the question carefully and provide an answer that directly addresses what is being asked.'
        elif word_count >= 2:
            score = 2
            status = 'Needs Improvement'
            feedback = 'Your answer is very brief and does not adequately explain the concept.'
            improvement = 'Review the foundational principles of this topic and write a complete explanation.'
        else:
            score = 0
            status = 'Not Good / Mismatched Answer'
            feedback = 'Your answer is insufficient to evaluate.'
            improvement = 'Provide a full, thoughtful response that addresses the core topic of the question.'

    # Sub-scores aligned with overall 0-10 score
    if score == 0:
        tech_k = 0
        comm = 0
        conf = 0
        rel = 0
        clar = 0
        prob = 0
    else:
        def sub(base, variance=1):
            v = base + random.choice([-1, 0, 0, 1]) if variance else base
            return max(0, min(10, v))

        tech_k = sub(score)
        comm = sub(min(10, score + (1 if sentence_count >= 2 else 0)))
        conf = sub(min(10, score + (1 if word_count >= 20 else 0)))
        rel = sub(min(10, score + 1 if match_count >= 2 else score))
        clar = sub(min(10, score + (1 if sentence_count >= 2 else -1 if word_count < 8 else 0)))
        prob = sub(score)

    return {
        'score': score,
        'technical_knowledge': tech_k,
        'communication': comm,
        'confidence': conf,
        'relevance': rel,
        'clarity': clar,
        'problem_solving': prob,
        'status': status,
        'feedback': feedback,
        'perfect_answer': perfect,
        'improvement': improvement,
    }


def _fallback_generate_followup(question, answer):
    """Generate a simple follow-up based on templates."""
    words = answer.split()
    # Extract a "topic" — take a meaningful phrase from the answer
    if len(words) > 5:
        start = random.randint(0, max(0, len(words) - 4))
        topic = ' '.join(words[start:start + 3])
    else:
        topic = ' '.join(words[:3]) if words else "that"

    template = random.choice(FOLLOWUP_TEMPLATES)

    if '{scenario}' in template:
        scenarios = [
            "the requirements changed midway",
            "you had limited time and resources",
            "you were working with a remote team",
            "the technology stack was different",
            "you had to present it to non-technical people",
        ]
        return template.format(scenario=random.choice(scenarios))

    return template.format(topic=topic)


def _fallback_final_feedback(questions_data, interview_type):
    """Generate rule-based final feedback with consistent 0-100 scoring."""
    if not questions_data:
        return {
            'feedback_summary': 'No questions were answered in this session.',
            'strengths': [],
            'weaknesses': ['No responses provided'],
            'improvements': ['Practice answering interview questions'],
            'recommendations': ['Start with basic interview preparation guides'],
            'readiness_pct': 0,
        }

    norm = lambda s: (s * 10 if s <= 10 else s) if s is not None else 0

    answered_questions = [q for q in questions_data if q.get('answer_text')]
    if not answered_questions:
        return {
            'feedback_summary': 'Interview concluded. No answers were submitted in this session.',
            'strengths': ['Attempted interview session'],
            'weaknesses': ['No answers provided'],
            'improvements': ['Practice typing or speaking answers for each question'],
            'recommendations': ['Review the question bank and practice responses'],
            'readiness_pct': 0,
        }

    scores = [norm(q.get('score', 0)) for q in answered_questions]
    avg_score = sum(scores) / len(scores) if scores else 0

    # Determine scores per category normalized to 0-100 scale
    categories = {
        'technical_knowledge': [],
        'communication': [],
        'confidence': [],
        'relevance': [],
        'clarity': [],
        'problem_solving': [],
    }
    for q in answered_questions:
        for cat in categories:
            val = q.get(cat)
            if val is not None:
                categories[cat].append(norm(val))

    cat_avgs = {}
    for cat, vals in categories.items():
        cat_avgs[cat] = sum(vals) / len(vals) if vals else avg_score

    # Sort categories by score
    sorted_cats = sorted(cat_avgs.items(), key=lambda x: x[1], reverse=True)
    cat_labels = {
        'technical_knowledge': 'Technical Knowledge',
        'communication': 'Communication Skills',
        'confidence': 'Confidence',
        'relevance': 'Answer Relevance',
        'clarity': 'Clarity of Expression',
        'problem_solving': 'Problem Solving',
    }

    # Strengths: categories scoring >= 70
    strengths = [cat_labels.get(c, c) for c, s in sorted_cats if s >= 70][:3]
    # Weaknesses: categories scoring < 65
    weaknesses = [cat_labels.get(c, c) for c, s in sorted(sorted_cats, key=lambda x: x[1]) if s < 65][:2]

    if not strengths:
        if sorted_cats and sorted_cats[0][1] >= 50:
            strengths = [cat_labels.get(sorted_cats[0][0], sorted_cats[0][0])]
        else:
            strengths = ['Willingness to attempt all questions']
    if not weaknesses:
        weaknesses = ['Minor improvements needed in detailed explanations']

    # Generate feedback summary based on 0-100 avg_score
    if avg_score >= 80:
        summary = f"Excellent performance! You demonstrated strong skills across the {interview_type} interview. Your answers were well-structured and showed good depth of knowledge. You're well-prepared for real interviews."
    elif avg_score >= 60:
        summary = f"Good performance in the {interview_type} interview. You showed solid understanding in several areas. With some focused practice on your weaker areas, you'll be well-prepared for real interviews."
    elif avg_score >= 40:
        summary = f"Fair performance in the {interview_type} interview. You have a foundation to build upon. Focus on providing more detailed answers with specific examples. Regular practice will help improve your scores significantly."
    else:
        summary = f"You've taken the first step by attempting this {interview_type} interview. Focus on building your foundational knowledge and practice answering questions with more detail and specific examples. Consider studying the recommended topics below."

    improvements = []
    if cat_avgs.get('communication', 50) < 60:
        improvements.append("Practice articulating your thoughts in a structured manner — use the STAR method for behavioral questions.")
    if cat_avgs.get('technical_knowledge', 50) < 60:
        improvements.append("Review fundamental concepts in your domain and practice explaining them clearly.")
    if cat_avgs.get('confidence', 50) < 60:
        improvements.append("Build confidence by practicing with peers and recording yourself answering questions.")
    if cat_avgs.get('relevance', 50) < 60:
        improvements.append("Focus on understanding the question fully before answering. Address the specific question asked.")
    if cat_avgs.get('clarity', 50) < 60:
        improvements.append("Work on structuring your answers with a clear beginning, middle, and conclusion.")
    if cat_avgs.get('problem_solving', 50) < 60:
        improvements.append("Practice breaking down complex problems into smaller, manageable steps.")
    if not improvements:
        improvements = ["Continue practicing to maintain and improve your strong performance.", "Try harder difficulty levels to challenge yourself further."]

    recommendations_map = {
        'hr': ['STAR Interview Method', 'Behavioral Interview Questions Guide', 'Emotional Intelligence in Interviews', 'Body Language Tips'],
        'technical': ['Data Structures & Algorithms', 'System Design Fundamentals', 'Design Patterns', 'Database Concepts'],
        'coding': ['LeetCode Practice Problems', 'Algorithm Complexity Analysis', 'Clean Code Principles', 'Problem-Solving Strategies'],
        'communication': ['Public Speaking Fundamentals', 'Active Listening Techniques', 'Business Communication Skills', 'Presentation Skills'],
        'general': ['Interview Preparation Guide', 'Industry Trends & Current Affairs', 'Critical Thinking Skills', 'Professional Development'],
    }
    recommendations = recommendations_map.get(interview_type.lower(), recommendations_map['general'])

    completion_factor = min(1.0, len(answered_questions) / max(1, len(questions_data)))
    readiness = int(round(avg_score * 0.9 * completion_factor + (10 * completion_factor)))
    readiness = min(100, max(0, readiness))

    return {
        'feedback_summary': summary,
        'strengths': strengths,
        'weaknesses': weaknesses,
        'improvements': improvements[:4],
        'recommendations': recommendations[:4],
        'readiness_pct': readiness,
    }
    