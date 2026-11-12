"""
J.A.R.V.I.S. Software Engineering Capabilities (31-45).
Autonomous Coding, Repo Understanding, Debugging, Test Generation & Execution,
Code Review, Architecture, Dependencies, Docs, Git, Deployment,
Build Diagnostics, Database Intelligence, API Testing, Refactoring.
"""

from .coding_agent import AutonomousCodingAgent
from .repo_analyzer import RepoAnalyzer
from .debugger import AutomatedDebugger
from .test_gen import TestGenerator
from .test_runner import TestRunner
from .code_reviewer import CodeReviewer
from .architecture import ArchitectureAnalyzer
from .dependencies import DependencyAnalyzer
from .doc_gen import DocumentationGenerator
from .git_intelligence import GitIntelligence
from .deployment import DeploymentAssistant
from .build_diagnostics import BuildDiagnostics
from .db_intelligence import DatabaseIntelligence
from .api_tester import APITester
from .refactoring import RefactoringAgent
from .engine import SoftwareEngineeringNexus, nexus

__all__ = [
    "AutonomousCodingAgent",
    "RepoAnalyzer",
    "AutomatedDebugger",
    "TestGenerator",
    "TestRunner",
    "CodeReviewer",
    "ArchitectureAnalyzer",
    "DependencyAnalyzer",
    "DocumentationGenerator",
    "GitIntelligence",
    "DeploymentAssistant",
    "BuildDiagnostics",
    "DatabaseIntelligence",
    "APITester",
    "RefactoringAgent",
    "SoftwareEngineeringNexus",
    "nexus",
]
