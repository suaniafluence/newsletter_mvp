"""
Définition de la Crew pour la génération automatique de newsletters
"""

from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.search_tool import search_articles
from .tools.internal_data_tool import load_internal_documents
from .tools.email_sender_tool import send_email


@CrewBase
class NewsletterMvpCrew:
    """Crew pour la génération automatique de newsletters personnalisées"""

    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"

    # === AGENTS ===

    @agent
    def collector_externe(self) -> Agent:
        return Agent(
            config=self.agents_config["collector_externe"],
            tools=[search_articles],
            verbose=True,
        )

    @agent
    def collector_interne(self) -> Agent:
        return Agent(
            config=self.agents_config["collector_interne"],
            tools=[load_internal_documents],
            verbose=True,
        )

    @agent
    def resumeur(self) -> Agent:
        return Agent(
            config=self.agents_config["resumeur"],
            verbose=True,
        )

    @agent
    def planificateur(self) -> Agent:
        return Agent(
            config=self.agents_config["planificateur"],
            verbose=True,
        )

    @agent
    def redacteur(self) -> Agent:
        return Agent(
            config=self.agents_config["redacteur"],
            verbose=True,
        )

    @agent
    def validateur(self) -> Agent:
        return Agent(
            config=self.agents_config["validateur"],
            verbose=True,
        )

    @agent
    def personnaliseur(self) -> Agent:
        return Agent(
            config=self.agents_config["personnaliseur"],
            verbose=True,
        )

    @agent
    def diffuseur(self) -> Agent:
        return Agent(
            config=self.agents_config["diffuseur"],
            tools=[send_email],
            verbose=True,
        )

    # === TASKS ===

    @task
    def collect_web_content(self) -> Task:
        return Task(
            config=self.tasks_config["collect_web_content"],
            agent=self.collector_externe(),
        )

    @task
    def collect_internal_content(self) -> Task:
        return Task(
            config=self.tasks_config["collect_internal_content"],
            agent=self.collector_interne(),
        )

    @task
    def summarize_content(self) -> Task:
        return Task(
            config=self.tasks_config["summarize_content"],
            agent=self.resumeur(),
        )

    @task
    def plan_newsletter(self) -> Task:
        return Task(
            config=self.tasks_config["plan_newsletter"],
            agent=self.planificateur(),
        )

    @task
    def write_newsletter(self) -> Task:
        return Task(
            config=self.tasks_config["write_newsletter"],
            agent=self.redacteur(),
        )

    @task
    def validate_newsletter(self) -> Task:
        return Task(
            config=self.tasks_config["validate_newsletter"],
            agent=self.validateur(),
        )

    @task
    def customize_newsletter(self) -> Task:
        return Task(
            config=self.tasks_config["customize_newsletter"],
            agent=self.personnaliseur(),
        )

    @task
    def send_newsletter(self) -> Task:
        return Task(
            config=self.tasks_config["send_newsletter"],
            agent=self.diffuseur(),
        )

    # === CREW ===

    @crew
    def crew(self) -> Crew:
        """Crée la crew avec tous les agents et tâches en séquence"""
        return Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
        )
