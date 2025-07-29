# Sequor
Sequor is a SQL-centric workflow platform for building reliable API integrations in modern data stacks. It's the open alternative to black-box SaaS connectors, giving data teams complete control over their integration pipelines.

Sequor fuses API execution with your database, enabling bidirectional data flow between APIs and database tables. By storing intermediate data in your database, you can leverage the full power of SQL for transformations, analytics, and business logic. This unified execution model eliminates the traditional boundary between iPaaS-style app integration and ETL-style data pipelines.

With Sequor's code-first approach (YAML for flows, Jinja or Python for dynamic parameters, and SQL for logic), you can apply software engineering best practices to integrations: version control, collaboration, CI/CD, and local development.

**Own**, **control**, and **scale** your integrations with transparent configuration, familiar open technologies, and without SaaS lock-in.

# How Sequor works
Sequor is designed around an intuitive YAML-based workflow definition. Every integration  flow is built from these powerful components:

* http_request - Execute API calls with database integration that iterates over input records, performs dynamic HTTP requests, and maps responses back to database tables. Use Jinja templates or Python snippets for dynamic parameterization.
* transform - Apply SQL queries to prepare data for API calls or process API results, leveraging the full power of your database for data manipulation.
* control statements - Build robust workflows with if-then-else conditionals, while loops, try-catch error handling, and more. These high-level orchestration capabilities ensure your integrations handle edge cases gracefully without custom code.

View [examples of these operations](https://sequor.dev/#example-snippets) in action, demonstrating how easy it is to build sophisticated integrations with Sequor.

# Getting started
* [Install Sequor](https://docs.sequor.dev/getting-started/installation). It is easy to start with `pip install sequor`.
* [Follow Quickstart](https://docs.sequor.dev/getting-started/quickstart)
* [Explore examples of real-life integrations](https://github.com/paloaltodatabases/sequor-integrations)
* [Documentation](https://docs.sequor.dev/)

# Community
* [Discuss Sequor on GitHub](https://github.com/paloaltodatabases/sequor/discussions) - To get help and participate in discussions about best practices, or any other conversation that would benefit from being searchable

# Stay connected
* [Subsribe to our newsletter](https://buttondown.com/sequor) -  updated on new releases and features, guides, and case studies.






  
