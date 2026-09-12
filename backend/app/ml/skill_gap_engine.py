import math
import re
from typing import Any, Dict, List, Optional, Set
from sqlalchemy.orm import Session
from app.models.enums import OpportunityCategory
from app.models.opportunity import Opportunity
from app.models.student_profile import StudentProfile
from app.services.skill_normalizer import SkillNormalizationService
from app.ml.skill_matcher import calculate_skill_match

# Standard Career Role Taxonomies and Competency Benchmarks
CAREER_BENCHMARKS = {
    "machine learning engineer": {
        "title": "Machine Learning Engineer",
        "domain": "AI / Machine Learning",
        "required_skills": [
            "Python", "PyTorch", "Machine Learning", "Deep Learning",
            "FastAPI", "Docker", "SQL", "Git", "Data Structures & Algorithms"
        ],
        "skill_metadata": {
            "Python": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "Object-oriented & asynchronous programming, numerical compute."},
            "PyTorch": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 2, "desc": "Custom autograd functions, distributed DDP, model training."},
            "Machine Learning": {"level": "Intermediate", "demand": 95, "priority": "High", "dep": 1, "desc": "Supervised, unsupervised algorithms, cross-validation."},
            "Deep Learning": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 2, "desc": "Transformers, CNNs, attention mechanisms, embeddings."},
            "FastAPI": {"level": "Intermediate", "demand": 85, "priority": "Medium", "dep": 2, "desc": "High-throughput model serving and REST microservices."},
            "Docker": {"level": "Intermediate", "demand": 88, "priority": "High", "dep": 2, "desc": "Containerization and reproducible runtime environments."},
            "SQL": {"level": "Intermediate", "demand": 82, "priority": "Medium", "dep": 1, "desc": "Analytical data querying and feature storage schemas."},
            "Git": {"level": "Intermediate", "demand": 90, "priority": "Medium", "dep": 1, "desc": "Branching workflows, version control, PR reviews."},
            "Data Structures & Algorithms": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 1, "desc": "Algorithmic complexity, memory management, graph traversal."},
        },
    },
    "data scientist": {
        "title": "Data Scientist",
        "domain": "Data Science & Analytics",
        "required_skills": [
            "Python", "SQL", "Pandas", "NumPy", "Machine Learning",
            "Data Analysis", "Tableau", "Power BI", "Data Structures & Algorithms"
        ],
        "skill_metadata": {
            "Python": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 1, "desc": "Statistical computation, ETL pipelines, analysis scripts."},
            "SQL": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "Complex joins, window functions, query performance optimization."},
            "Pandas": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 2, "desc": "Dataframe transformations, aggregation, time series."},
            "NumPy": {"level": "Intermediate", "demand": 90, "priority": "Medium", "dep": 2, "desc": "Vectorized linear algebra, array broadcasting."},
            "Machine Learning": {"level": "Intermediate", "demand": 88, "priority": "High", "dep": 2, "desc": "Predictive modeling, regression, clustering."},
            "Data Analysis": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 1, "desc": "Hypothesis testing, exploratory data analysis."},
            "Tableau": {"level": "Intermediate", "demand": 80, "priority": "Medium", "dep": 2, "desc": "Executive dashboarding and metric tracking."},
            "Power BI": {"level": "Intermediate", "demand": 78, "priority": "Medium", "dep": 2, "desc": "Business intelligence modeling and report delivery."},
            "Data Structures & Algorithms": {"level": "Intermediate", "demand": 84, "priority": "Medium", "dep": 1, "desc": "Efficient data traversal, searching, hashing."},
        },
    },
    "full-stack developer": {
        "title": "Full-Stack Developer",
        "domain": "Web Technologies",
        "required_skills": [
            "JavaScript", "TypeScript", "React", "Node.js", "Express.js",
            "TailwindCSS", "SQL", "REST APIs", "Git", "Docker"
        ],
        "skill_metadata": {
            "JavaScript": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "ES6+ semantics, async/await, DOM, closures."},
            "TypeScript": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 2, "desc": "Static typing, generics, strict null checking."},
            "React": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 2, "desc": "Component architecture, hooks, state management."},
            "Node.js": {"level": "Intermediate", "demand": 90, "priority": "High", "dep": 2, "desc": "Event-driven runtime, streams, server performance."},
            "Express.js": {"level": "Intermediate", "demand": 85, "priority": "Medium", "dep": 3, "desc": "Routing, middleware pipelines, authentication."},
            "TailwindCSS": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 2, "desc": "Utility-first responsive styling and design systems."},
            "SQL": {"level": "Intermediate", "demand": 84, "priority": "Medium", "dep": 1, "desc": "Relational schemas, ORM integrations."},
            "REST APIs": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 2, "desc": "Contract design, error handling, status semantics."},
            "Git": {"level": "Intermediate", "demand": 90, "priority": "Medium", "dep": 1, "desc": "Version control, GitFlow, code reviews."},
            "Docker": {"level": "Intermediate", "demand": 82, "priority": "Medium", "dep": 2, "desc": "Containerized development and staging environments."},
        },
    },
    "cloud solutions architect": {
        "title": "Cloud Solutions Architect",
        "domain": "Cloud & DevOps",
        "required_skills": [
            "AWS", "Docker", "Kubernetes", "Linux", "CI/CD",
            "System Design", "Python", "SQL", "Cybersecurity"
        ],
        "skill_metadata": {
            "AWS": {"level": "Advanced", "demand": 97, "priority": "High", "dep": 2, "desc": "VPC, IAM, ECS, EKS, Lambda, S3 infrastructure."},
            "Docker": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 1, "desc": "Multi-stage builds, container isolation."},
            "Kubernetes": {"level": "Intermediate", "demand": 92, "priority": "High", "dep": 2, "desc": "Pod scheduling, ingress, Helm charts, autoscaling."},
            "Linux": {"level": "Advanced", "demand": 90, "priority": "High", "dep": 1, "desc": "Shell scripting, process management, networking."},
            "CI/CD": {"level": "Intermediate", "demand": 88, "priority": "High", "dep": 2, "desc": "Automated pipelines, GitHub Actions, Jenkins."},
            "System Design": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 2, "desc": "High availability, fault tolerance, caching."},
            "Python": {"level": "Intermediate", "demand": 84, "priority": "Medium", "dep": 1, "desc": "Cloud automation scripts, SDK tooling."},
            "SQL": {"level": "Intermediate", "demand": 80, "priority": "Medium", "dep": 1, "desc": "Database tier provisioning, read replicas."},
            "Cybersecurity": {"level": "Intermediate", "demand": 86, "priority": "High", "dep": 2, "desc": "Zero trust, encryption in transit/at rest."},
        },
    },
    "cybersecurity analyst": {
        "title": "Cybersecurity Analyst",
        "domain": "Cybersecurity & Networks",
        "required_skills": [
            "Cybersecurity", "Computer Networks", "Linux", "Python",
            "Bash", "Operating Systems", "SQL"
        ],
        "skill_metadata": {
            "Cybersecurity": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 2, "desc": "Vulnerability scanning, SIEM, threat modeling."},
            "Computer Networks": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 1, "desc": "TCP/IP, DNS, subnetting, Wireshark packet capture."},
            "Linux": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 1, "desc": "System auditing, permissions, firewalls (iptables)."},
            "Python": {"level": "Intermediate", "demand": 85, "priority": "Medium", "dep": 1, "desc": "Security automation, log parsing, exploit analysis."},
            "Bash": {"level": "Intermediate", "demand": 84, "priority": "Medium", "dep": 1, "desc": "Automated reconnaissance, system administration."},
            "Operating Systems": {"level": "Advanced", "demand": 88, "priority": "High", "dep": 1, "desc": "Process memory layout, buffer management."},
            "SQL": {"level": "Intermediate", "demand": 80, "priority": "Medium", "dep": 1, "desc": "SQL injection detection, database audit logs."},
        },
    },
    # Mechanical Engineering Roles
    "mechanical design engineer": {
        "title": "Mechanical Design Engineer",
        "domain": "Mechanical & Aerospace Engineering",
        "required_skills": [
            "CAD", "SolidWorks", "Finite Element Analysis", "ANSYS",
            "GD&T", "DFM", "Thermodynamics", "Materials Science", "MATLAB"
        ],
        "skill_metadata": {
            "CAD": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "3D parametric modeling, complex assemblies, design documentation."},
            "SolidWorks": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 1, "desc": "Part modeling, surfacing, sheet metal, and simulation toolsets."},
            "Finite Element Analysis": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 2, "desc": "Stress/strain distribution, modal frequency, mesh convergence."},
            "ANSYS": {"level": "Intermediate", "demand": 92, "priority": "High", "dep": 2, "desc": "Structural mechanics, thermal simulation, CFD analysis."},
            "GD&T": {"level": "Advanced", "demand": 90, "priority": "High", "dep": 1, "desc": "ASME Y14.5 geometric dimensioning, tolerancing, datums, CMM."},
            "DFM": {"level": "Intermediate", "demand": 88, "priority": "Medium", "dep": 2, "desc": "Design for manufacturing, injection molding, CNC machining."},
            "Thermodynamics": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 1, "desc": "Heat transfer, fluid flow cycles, thermal dissipation."},
            "Materials Science": {"level": "Intermediate", "demand": 85, "priority": "Medium", "dep": 1, "desc": "Alloy selection, tensile yield, fatigue limits, polymers."},
            "MATLAB": {"level": "Intermediate", "demand": 82, "priority": "Medium", "dep": 1, "desc": "Numerical modeling, kinematics simulation, data analysis."},
        },
    },
    "robotics & mechatronics engineer": {
        "title": "Robotics & Mechatronics Engineer",
        "domain": "Robotics & Automation",
        "required_skills": [
            "Robotics", "ROS", "Python", "C++", "CAD",
            "Microcontrollers", "Kinematics", "MATLAB", "Sensors"
        ],
        "skill_metadata": {
            "Robotics": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "Actuators, motor drivers, sensor fusion, state estimation."},
            "ROS": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 2, "desc": "ROS2 nodes, publishers/subscribers, navigation stacks, URDF."},
            "C++": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 1, "desc": "Real-time control loops, low-latency execution, memory control."},
            "Python": {"level": "Intermediate", "demand": 90, "priority": "Medium", "dep": 1, "desc": "High-level planning, simulation scripting, data visualization."},
            "CAD": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 1, "desc": "Chassis and end-effector 3D modeling."},
            "Microcontrollers": {"level": "Intermediate", "demand": 92, "priority": "High", "dep": 1, "desc": "STM32, ESP32, PWM signal generation, GPIO interfaces."},
            "Kinematics": {"level": "Advanced", "demand": 88, "priority": "High", "dep": 2, "desc": "Forward/inverse kinematics, Jacobian matrices, motion planning."},
            "MATLAB": {"level": "Intermediate", "demand": 84, "priority": "Medium", "dep": 1, "desc": "Simulink control block modeling, PID controller tuning."},
            "Sensors": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 1, "desc": "LiDAR, IMU, ultrasonic, encoders, I2C/SPI calibration."},
        },
    },
    "automotive & ev systems engineer": {
        "title": "Automotive & EV Systems Engineer",
        "domain": "Automotive & Clean Mobility",
        "required_skills": [
            "EV Powertrain", "Thermodynamics", "MATLAB", "CAD",
            "SolidWorks", "Finite Element Analysis", "Circuit Design", "CAN Bus"
        ],
        "skill_metadata": {
            "EV Powertrain": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 2, "desc": "Battery thermal management, BMS, motor inverter integration."},
            "Thermodynamics": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 1, "desc": "Heat exchanger sizing, coolant loop optimization, phase change."},
            "MATLAB": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 1, "desc": "Vehicle dynamics simulation, drive-cycle energy calculations."},
            "CAD": {"level": "Intermediate", "demand": 90, "priority": "Medium", "dep": 1, "desc": "Pack packaging, structural cradle modeling."},
            "SolidWorks": {"level": "Intermediate", "demand": 88, "priority": "Medium", "dep": 1, "desc": "Mechanical mounting, collision crashworthiness."},
            "Finite Element Analysis": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 2, "desc": "Vibration harmonics, chassis torsion analysis."},
            "Circuit Design": {"level": "Intermediate", "demand": 84, "priority": "Medium", "dep": 1, "desc": "High-voltage distribution, contactor relay circuits."},
            "CAN Bus": {"level": "Intermediate", "demand": 89, "priority": "High", "dep": 2, "desc": "Vehicle network protocol telemetry, diagnostic trouble codes."},
        },
    },

    # Electrical & Electronics Engineering Roles
    "embedded systems engineer": {
        "title": "Embedded Systems Engineer",
        "domain": "Electrical & Embedded Engineering",
        "required_skills": [
            "Embedded C", "Embedded Systems", "Microcontrollers", "STM32",
            "RTOS", "Circuit Design", "PCB Design", "Hardware Debugging", "C++"
        ],
        "skill_metadata": {
            "Embedded C": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "Bare-metal registers, bitwise manipulation, interrupt service routines."},
            "Embedded Systems": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 1, "desc": "Hardware-software co-design, timers, DMA, bootloaders."},
            "Microcontrollers": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 1, "desc": "ARM Cortex-M architectures, memory maps, power modes."},
            "STM32": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 2, "desc": "STM32CubeIDE, HAL drivers, peripheral clock configuration."},
            "RTOS": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 2, "desc": "FreeRTOS task scheduling, mutexes, semaphores, queues."},
            "Circuit Design": {"level": "Intermediate", "demand": 88, "priority": "Medium", "dep": 1, "desc": "Schematic capture, power regulation, decoupling capacitors."},
            "PCB Design": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 2, "desc": "Altium/KiCad trace routing, signal integrity, ground planes."},
            "Hardware Debugging": {"level": "Intermediate", "demand": 90, "priority": "High", "dep": 1, "desc": "Oscilloscopes, logic analyzers, JTAG/SWD debug probes."},
            "C++": {"level": "Intermediate", "demand": 84, "priority": "Medium", "dep": 1, "desc": "Modern embedded C++17, RAII, zero-cost abstractions."},
        },
    },
    "vlsi design engineer": {
        "title": "VLSI Design Engineer",
        "domain": "Semiconductor & VLSI",
        "required_skills": [
            "Verilog", "VHDL", "FPGA", "VLSI", "Digital Electronics",
            "Computer Architecture", "Static Timing Analysis", "C"
        ],
        "skill_metadata": {
            "Verilog": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "RTL synthesis, testbench generation, finite state machines."},
            "VHDL": {"level": "Intermediate", "demand": 90, "priority": "Medium", "dep": 1, "desc": "Structural and behavioral hardware description."},
            "FPGA": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 2, "desc": "Xilinx Vivado, Intel Quartus, timing constraints, bitstreams."},
            "VLSI": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 2, "desc": "CMOS logic, layout rules, ASIC fabrication workflow."},
            "Digital Electronics": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 1, "desc": "Boolean logic minimization, sequential circuits, flip-flops."},
            "Computer Architecture": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 1, "desc": "RISC-V/MIPS pipeline stages, hazard detection, caches."},
            "Static Timing Analysis": {"level": "Intermediate", "demand": 88, "priority": "High", "dep": 2, "desc": "Setup/hold times, clock skew, critical path optimization."},
            "C": {"level": "Intermediate", "demand": 84, "priority": "Medium", "dep": 1, "desc": "Hardware emulation models, firmware verification."},
        },
    },
    "power & renewable energy engineer": {
        "title": "Power & Renewable Energy Engineer",
        "domain": "Power Systems & Renewables",
        "required_skills": [
            "Power Electronics", "Circuit Design", "MATLAB", "Electrical Grid",
            "Inverters", "Renewable Energy", "Sensors", "CAD"
        ],
        "skill_metadata": {
            "Power Electronics": {"level": "Advanced", "demand": 97, "priority": "High", "dep": 1, "desc": "Buck/boost converters, MOSFET/IGBT gate drivers, PFC circuits."},
            "Circuit Design": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 1, "desc": "High-voltage schematic capture, transformer winding design."},
            "MATLAB": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 1, "desc": "Simulink Simscape Power Systems grid transient modeling."},
            "Electrical Grid": {"level": "Intermediate", "demand": 90, "priority": "High", "dep": 2, "desc": "Three-phase power flow, synchronization, sub-station safety."},
            "Inverters": {"level": "Intermediate", "demand": 88, "priority": "High", "dep": 2, "desc": "PWM solar grid-tie inverters, harmonic THD minimization."},
            "Renewable Energy": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 1, "desc": "Photovoltaic array MPPT tracking, wind turbine dynamics."},
            "Sensors": {"level": "Intermediate", "demand": 82, "priority": "Medium", "dep": 1, "desc": "Hall effect current transducers, voltage divider calibration."},
            "CAD": {"level": "Intermediate", "demand": 80, "priority": "Medium", "dep": 1, "desc": "Enclosure packaging, thermal heat-sink mounting."},
        },
    },

    # Finance, Banking & Analytics Roles
    "financial analyst": {
        "title": "Financial Analyst",
        "domain": "Corporate Finance & Banking",
        "required_skills": [
            "Financial Modeling", "Valuation", "Excel", "Corporate Finance",
            "Financial Statement Analysis", "Accounting", "DCF", "Power BI"
        ],
        "skill_metadata": {
            "Financial Modeling": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 2, "desc": "3-statement integrated dynamic models, scenario forecasting."},
            "Valuation": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 2, "desc": "Discounted cash flow (DCF), trading multiples, precedent transactions."},
            "Excel": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "INDEX/MATCH, dynamic arrays, sensitivity data tables, macros."},
            "Corporate Finance": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 1, "desc": "Capital budgeting, WACC, working capital management, debt sizing."},
            "Financial Statement Analysis": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 1, "desc": "Ratio analysis, GAAP/IFRS nuances, cash conversion cycle."},
            "Accounting": {"level": "Intermediate", "demand": 90, "priority": "High", "dep": 1, "desc": "Debits/credits, balance sheet reconciliation, accruals."},
            "DCF": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 2, "desc": "Free cash flow projection, terminal value, enterprise valuation."},
            "Power BI": {"level": "Intermediate", "demand": 82, "priority": "Medium", "dep": 2, "desc": "Executive board reporting, automated KPI refreshes."},
        },
    },
    "quantitative finance analyst": {
        "title": "Quantitative Finance Analyst",
        "domain": "Quantitative Finance & Trading",
        "required_skills": [
            "Python", "Quantitative Finance", "SQL", "Pandas",
            "Algorithmic Trading", "Statistics", "Risk Management", "C++"
        ],
        "skill_metadata": {
            "Python": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 1, "desc": "Vectorized time series, quantitative backtesting engines."},
            "Quantitative Finance": {"level": "Advanced", "demand": 97, "priority": "High", "dep": 2, "desc": "Black-Scholes option pricing, stochastic calculus, risk neutral."},
            "SQL": {"level": "Advanced", "demand": 92, "priority": "High", "dep": 1, "desc": "Tick database aggregation, order book trade reconstruction."},
            "Pandas": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 1, "desc": "High-frequency time-series resampling, rolling Sharpe ratios."},
            "Algorithmic Trading": {"level": "Intermediate", "demand": 90, "priority": "High", "dep": 2, "desc": "Execution algorithms (TWAP/VWAP), market microstructure."},
            "Statistics": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 1, "desc": "Monte Carlo simulations, hypothesis testing, GARCH models."},
            "Risk Management": {"level": "Intermediate", "demand": 88, "priority": "Medium", "dep": 2, "desc": "Value at Risk (VaR), stress testing, drawdown monitoring."},
            "C++": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 1, "desc": "Ultra low latency pricing logic, memory caching."},
        },
    },
    "equity research & investment analyst": {
        "title": "Equity Research & Investment Analyst",
        "domain": "Asset Management & Markets",
        "required_skills": [
            "Equity Research", "Valuation", "Financial Modeling", "Corporate Finance",
            "Financial Statement Analysis", "Excel", "Bloomberg Terminal", "Accounting"
        ],
        "skill_metadata": {
            "Equity Research": {"level": "Advanced", "demand": 98, "priority": "High", "dep": 2, "desc": "Initiation reports, quarterly earnings reviews, sector coverage."},
            "Valuation": {"level": "Advanced", "demand": 96, "priority": "High", "dep": 2, "desc": "Sum-of-the-parts (SOTP), target price derivation, multiples."},
            "Financial Modeling": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 2, "desc": "Revenue driver builds, unit economics, sensitivity models."},
            "Corporate Finance": {"level": "Intermediate", "demand": 92, "priority": "High", "dep": 1, "desc": "Capital allocation, share repurchases, dividends."},
            "Financial Statement Analysis": {"level": "Advanced", "demand": 94, "priority": "High", "dep": 1, "desc": "Margin expansion drivers, forensic accounting audits."},
            "Excel": {"level": "Advanced", "demand": 95, "priority": "High", "dep": 1, "desc": "Clean financial formatting, dynamic chart generation."},
            "Bloomberg Terminal": {"level": "Intermediate", "demand": 86, "priority": "Medium", "dep": 2, "desc": "Company filings (CF), consensus estimates (EE), market news."},
            "Accounting": {"level": "Intermediate", "demand": 90, "priority": "High", "dep": 1, "desc": "GAAP/non-GAAP adjustments, EBITDA reconciliation."},
        },
    },
}


def _normalize_role_key(raw_role: str) -> str:
    key = (raw_role or "").lower().strip()
    if re.search(r"\b(full[\s-]?stack|web|frontend|software|developer|dev|swe)\b", key):
        return "full-stack developer"
    if re.search(r"\b(mechanical|cad|solidworks|ansys|fea|thermodynamics)\b", key):
        return "mechanical design engineer"
    if re.search(r"\b(robot|robotics|mechatronic|mechatronics|ros)\b", key):
        return "robotics & mechatronics engineer"
    if re.search(r"\b(automotive|ev|electric vehicle|powertrain|vehicle)\b", key):
        return "automotive & ev systems engineer"
    if re.search(r"\b(embedded|microcontroller|firmware|stm32|rtos)\b", key):
        return "embedded systems engineer"
    if re.search(r"\b(vlsi|chip|asic|fpga|verilog|vhdl)\b", key):
        return "vlsi design engineer"
    if re.search(r"\b(power|electrical|renewable|solar|grid)\b", key):
        return "power & renewable energy engineer"
    if re.search(r"\b(quantitative|quant|algo trading|algorithmic)\b", key):
        return "quantitative finance analyst"
    if re.search(r"\b(equity|equity research|investment|investment banking|banking)\b", key):
        return "equity research & investment analyst"
    if re.search(r"\b(finance|financial|valuation|corporate finance)\b", key):
        return "financial analyst"
    if re.search(r"\b(data science|data scientist|data analyst|bi analyst)\b", key):
        return "data scientist"
    if re.search(r"\b(machine|machine learning|ai|artificial intelligence|ml|deep learning)\b", key):
        return "machine learning engineer"
    if re.search(r"\b(cloud|devops|architect|aws|azure)\b", key):
        return "cloud solutions architect"
    if re.search(r"\b(security|cyber|cybersecurity|infosec)\b", key):
        return "cybersecurity analyst"
    return "machine learning engineer"


def rank_priority_skills(
    missing_skills: List[str],
    skill_meta: Dict[str, Dict[str, Any]],
    student_skills: List[str],
    db_frequency_map: Optional[Dict[str, int]] = None,
) -> List[Dict[str, Any]]:
    """
    Ranks missing skills according to:
    1. Dependency order (foundational dep=1 before dep=2)
    2. Role importance / demand frequency
    3. Current student readiness (skills where student has partial background)
    """
    freq_map = db_frequency_map or {}
    ranked = []

    for s in missing_skills:
        meta = skill_meta.get(s, {})
        level = meta.get("level", "Intermediate")
        priority = meta.get("priority", "High")
        dep = meta.get("dep", 2)
        demand = meta.get("demand", 80)
        desc = meta.get("desc", f"Key competency in {s}.")

        # Factor in actual DB opportunity occurrences
        db_count = freq_map.get(s.lower(), 0)
        demand_score = demand + min(10, db_count * 2)

        ranked.append({
            "name": s,
            "level": level,
            "description": desc,
            "verificationNote": f"Recommended by Industry Benchmark ({demand_score}% Demand)",
            "progressPercent": 15 if dep == 1 else 5,
            "rolesDemandPercent": min(99, demand_score),
            "priority": priority,
            "dependency": dep,
        })

    # Sort: lower dependency (foundations first), then higher demand percentage
    ranked.sort(key=lambda x: (x["dependency"], -x["rolesDemandPercent"]))
    return ranked


def analyze_skill_gap_for_opportunity(
    db: Session,
    student_profile: StudentProfile,
    opportunity: Opportunity,
) -> Dict[str, Any]:
    """
    Analyzes skill gaps against a specific opportunity:
    - MATCHED: skills student has
    - MISSING: unmet required skills
    - PARTIAL: related skills providing partial credit
    - readiness percentage
    - priority ranked skills
    """
    student_skills = [ss.skill.name for ss in student_profile.skills if ss.skill]
    match_result = calculate_skill_match(
        student_skills=student_skills,
        required_skills=opportunity.required_skills or [],
        preferred_skills=opportunity.preferred_skills or [],
    )

    matched = match_result["matched_skills"]
    missing = match_result["missing_skills"]
    partial = match_result["partial_skills"]
    readiness = match_result["skill_match_percentage"]

    # Rank priority skills
    role_key = _normalize_role_key(opportunity.title + " " + opportunity.domain)
    meta = CAREER_BENCHMARKS.get(role_key, {}).get("skill_metadata", {})

    priority_skills = rank_priority_skills(
        missing_skills=missing,
        skill_meta=meta,
        student_skills=student_skills,
    )

    return {
        "opportunity_id": opportunity.id,
        "opportunity_title": opportunity.title,
        "organization": opportunity.organization,
        "readiness_percentage": readiness,
        "total_required_skills": len(opportunity.required_skills or []),
        "matched_skills": matched,
        "missing_skills": missing,
        "partial_skills": partial,
        "priority_skills": priority_skills,
        "estimated_weeks_to_close": f"{max(1, len(missing) * 2)}-{len(missing) * 3} weeks",
    }


def analyze_skill_gap_for_role(
    db: Session,
    student_profile: StudentProfile,
    role_name_or_id: Optional[str] = None,
) -> Dict[str, Any]:
    """
    Analyzes skill gap for a target career (e.g. Machine Learning Engineer, Full-Stack Developer).
    Returns TargetRoleGapData matching Stitch UI specifications.
    """
    role_key = _normalize_role_key(role_name_or_id or student_profile.target_role or "Machine Learning Engineer")
    benchmark = CAREER_BENCHMARKS[role_key]

    student_skills = [ss.skill.name for ss in student_profile.skills if ss.skill]
    match_result = calculate_skill_match(
        student_skills=student_skills,
        required_skills=benchmark["required_skills"],
    )

    matched = match_result["matched_skills"]
    missing = match_result["missing_skills"]
    partial = match_result["partial_skills"]

    meta = benchmark["skill_metadata"]

    # Mastered skills
    mastered = []
    for s in matched:
        m_info = meta.get(s, {})
        mastered.append({
            "name": s,
            "level": m_info.get("level", "Advanced"),
            "description": m_info.get("desc", f"Proficient competency in {s}."),
            "verificationNote": "Verified via profile coursework & assessment",
            "progressPercent": 90,
            "rolesDemandPercent": m_info.get("demand", 95),
            "priority": m_info.get("priority", "High"),
        })

    # Developing / Partial skills
    developing = []
    for p in partial:
        req_s = p["required_skill"]
        stud_s = p["student_skill"]
        m_info = meta.get(req_s, {})
        developing.append({
            "name": f"{req_s} (Foundation: {stud_s})",
            "level": "Intermediate",
            "description": f"Transferable proficiency from {stud_s}. Ready for framework transition.",
            "verificationNote": f"Verified competency via {stud_s}",
            "progressPercent": 65,
            "rolesDemandPercent": m_info.get("demand", 88),
            "priority": m_info.get("priority", "High"),
        })

    # Critical Gaps (Priority Ranked)
    critical_gaps = rank_priority_skills(missing, meta, student_skills)

    # Readiness computation
    total_req = len(benchmark["required_skills"])
    readiness = int(round(match_result["skill_match_percentage"]))

    # Find real employer benchmarks from actual database opportunities
    opps = db.query(Opportunity).filter(Opportunity.verified == True).all()
    employer_benchmarks = []
    for opp in opps[:6]:
        if benchmark["domain"].lower() in opp.domain.lower() or opp.category == OpportunityCategory.INTERNSHIP:
            employer_benchmarks.append({
                "company": opp.organization,
                "tier": "Tier 1 Enterprise",
                "role": opp.title,
                "matchScore": opp.match_score or 82,
                "statusNote": f"Target opportunity in {opp.location}",
                "isStrongFit": (opp.match_score or 0) >= 80,
            })
    if not employer_benchmarks:
        employer_benchmarks = [
            {
                "company": "TechNova Labs",
                "tier": "Tier 1 Global",
                "role": benchmark["title"],
                "matchScore": 84,
                "statusNote": "Strong fit for early-career placement",
                "isStrongFit": True,
            }
        ]

    weeks = f"{max(2, len(critical_gaps) * 2)}-{max(4, len(critical_gaps) * 3)} weeks"

    return {
        "roleId": role_key.replace(" ", "-"),
        "roleTitle": benchmark["title"],
        "readinessScore": readiness,
        "estimatedWeeksToClose": weeks,
        "competenciesMet": len(mastered) + len(developing),
        "competenciesTotal": total_req,
        "mastered": mastered,
        "developing": developing,
        "criticalGaps": critical_gaps,
        "employerBenchmarks": employer_benchmarks[:4],
    }


def recommend_learning_resources_for_gap(
    db: Session,
    student_profile: StudentProfile,
    opportunity_id: Optional[str] = None,
    role_title: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Recommends actual learning courses, projects, and certifications stored in the database
    that directly target the student's missing skills.
    """
    # 1. Determine missing skills
    if opportunity_id:
        opp = db.query(Opportunity).filter(Opportunity.id == opportunity_id).first()
        if opp:
            gap_analysis = analyze_skill_gap_for_opportunity(db, student_profile, opp)
            missing = gap_analysis["missing_skills"]
        else:
            missing = []
    else:
        gap_analysis = analyze_skill_gap_for_role(db, student_profile, role_title)
        missing = [g["name"] for g in gap_analysis["criticalGaps"]]

    missing_lower = {s.lower() for s in missing}

    # 2. Query database for learning opportunities (Courses, Projects, Skill Opportunities)
    learning_opps = (
        db.query(Opportunity)
        .filter(
            Opportunity.category.in_([
                OpportunityCategory.COURSE,
                OpportunityCategory.PROJECT,
                OpportunityCategory.SKILL_OPPORTUNITY,
            ])
        )
        .all()
    )

    resources = []
    for opp in learning_opps:
        # Check how many missing skills are covered
        opp_skills = [s.lower() for s in (opp.required_skills or []) + (opp.preferred_skills or [])]
        overlap = [s for s in missing_lower if s in opp_skills or s in opp.title.lower() or s in opp.description.lower()]
        
        addressed_skill = overlap[0].title() if overlap else (missing[0] if missing else "Core Technical Skills")
        
        # Calculate impact score based on overlap
        impact_boost = min(18, 6 + (len(overlap) * 4))
        
        r_type = "Course"
        if opp.category == OpportunityCategory.PROJECT:
            r_type = "Project"
        elif opp.category == OpportunityCategory.SKILL_OPPORTUNITY:
            r_type = "Certification"

        resources.append({
            "id": opp.id,
            "title": opp.title,
            "provider": opp.organization,
            "type": r_type,
            "addressesGap": addressed_skill,
            "duration": opp.duration or "4-6 Weeks",
            "impactScore": f"+{impact_boost}% Match Boost",
            "description": opp.description,
            "perks": opp.compensation or "Verified Credential",
            "imageUrl": opp.image_banner or "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800",
            "relevance": len(overlap),
        })

    # Sort by relevance to missing skills
    resources.sort(key=lambda x: x["relevance"], reverse=True)

    # Fallback if DB didn't have enough courses
    if not resources:
        primary_gap = missing[0] if missing else "Machine Learning Systems"
        resources.append({
            "id": "res-default-1",
            "title": f"Mastering {primary_gap} for Industry Applications",
            "provider": "SkillMatch Academy",
            "type": "Course",
            "addressesGap": primary_gap,
            "duration": "4 Weeks (Self-paced)",
            "impactScore": "+10% Match Boost",
            "description": f"Comprehensive hands-on curriculum bridging theoretical concepts into production {primary_gap}.",
            "perks": "Verified Completion Certificate",
            "imageUrl": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800",
        })

    return resources[:6]


def generate_career_roadmap(
    db: Session,
    student_profile: StudentProfile,
    target_career: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Generates an actionable, verified sequence representing:
    Current Profile -> Target Career -> Required Skills -> Missing Skills -> Learning -> Projects -> Opportunities.
    """
    role_key = _normalize_role_key(target_career or student_profile.target_role or "Machine Learning Engineer")
    benchmark = CAREER_BENCHMARKS[role_key]

    gap_data = analyze_skill_gap_for_role(db, student_profile, role_key)
    mastered = gap_data["mastered"]
    critical = gap_data["criticalGaps"]

    steps = []
    step_num = 1

    # 1. Profile Baseline / Foundational Competencies (Completed)
    mastered_names = [m["name"] for m in mastered[:3]]
    m_str = ", ".join(mastered_names) if mastered_names else "Core Academic Foundations"
    steps.append({
        "id": f"step-{step_num}",
        "stepNumber": step_num,
        "title": f"Foundational Competency in {benchmark['domain']}",
        "status": "completed",
        "statusLabel": "Completed",
        "description": f"Academic coursework and verified proficiency in {m_str}.",
        "tag": "Foundation",
        "meta": "Verified Baseline",
        "badge": "Verified",
    })
    step_num += 1

    # 2. Mastered Core Tools (Completed or In-Progress)
    steps.append({
        "id": f"step-{step_num}",
        "stepNumber": step_num,
        "title": "Core Programming & Version Control",
        "status": "completed",
        "statusLabel": "Completed",
        "description": "Clean code architecture, unit testing, Git branching workflows, and documentation.",
        "tag": "Tooling",
        "meta": "Completed Milestone",
    })
    step_num += 1

    # 3. Target Gap Learning Milestone (Current Step)
    if critical:
        primary_gap = critical[0]["name"]
        steps.append({
            "id": f"step-{step_num}",
            "stepNumber": step_num,
            "title": f"Master {primary_gap} Architecture & Best Practices",
            "status": "current",
            "statusLabel": "Current Focus",
            "description": f"Focused study and hands-on laboratory modules addressing critical requirement {primary_gap}.",
            "tag": "Upskilling",
            "meta": "Target: Next 3 Weeks",
            "badge": "Active",
        })
        step_num += 1

    # 4. Secondary Gap Learning
    if len(critical) > 1:
        sec_gap = critical[1]["name"]
        steps.append({
            "id": f"step-{step_num}",
            "stepNumber": step_num,
            "title": f"Build Proficiency in {sec_gap}",
            "status": "upcoming",
            "statusLabel": "Upcoming",
            "description": f"Bridge the competency gap in {sec_gap} using targeted database learning modules.",
            "tag": "Specialization",
            "meta": "Est: 4 Weeks",
        })
        step_num += 1

    # 5. Capstone Project Milestone
    domain_filter = benchmark.get("domain", "").split()[0] if benchmark.get("domain") else ""
    proj_opp = None
    if domain_filter:
        proj_opp = (
            db.query(Opportunity)
            .filter(
                Opportunity.category == OpportunityCategory.PROJECT,
                Opportunity.domain.ilike(f"%{domain_filter}%"),
            )
            .first()
        )
    if not proj_opp:
        proj_opp = (
            db.query(Opportunity)
            .filter(Opportunity.category == OpportunityCategory.PROJECT)
            .first()
        )
    proj_title = proj_opp.title if proj_opp else f"{benchmark['title']} Industry Portfolio Capstone"
    steps.append({
        "id": f"step-{step_num}",
        "stepNumber": step_num,
        "title": f"Deliver Hands-on Project: {proj_title}",
        "status": "upcoming",
        "statusLabel": "Upcoming",
        "description": f"Implement an end-to-end project applying all newly acquired skills to showcase on GitHub and verified portfolio.",
        "tag": "Portfolio",
        "meta": "Portfolio Artifact",
    })
    step_num += 1

    # 6. Industry Certification / Assessment
    steps.append({
        "id": f"step-{step_num}",
        "stepNumber": step_num,
        "title": f"{benchmark['title']} Industry Competency Benchmark",
        "status": "upcoming",
        "statusLabel": "Upcoming",
        "description": f"Take the standardized SkillMatch technical validation benchmark to earn employer-verified badge in {benchmark['domain']}.",
        "tag": "Certification",
        "meta": "Badge Verification",
    })
    step_num += 1

    # 7. Placement into Target Opportunity
    top_opp = None
    if domain_filter:
        top_opp = (
            db.query(Opportunity)
            .filter(
                Opportunity.verified == True,
                Opportunity.category.in_([OpportunityCategory.INTERNSHIP, OpportunityCategory.JOB]),
                Opportunity.domain.ilike(f"%{domain_filter}%"),
            )
            .first()
        )
    if not top_opp:
        top_opp = (
            db.query(Opportunity)
            .filter(
                Opportunity.verified == True,
                Opportunity.category.in_([OpportunityCategory.INTERNSHIP, OpportunityCategory.JOB]),
            )
            .first()
        )
    target_opp_title = f"{top_opp.title} at {top_opp.organization}" if top_opp else f"Senior {benchmark['title']} Placement"
    steps.append({
        "id": f"step-{step_num}",
        "stepNumber": step_num,
        "title": f"Target Placement: {target_opp_title}",
        "status": "upcoming",
        "statusLabel": "Target Milestone",
        "description": f"Submit verified portfolio application with 85%+ match confidence to Tier-1 industry employers.",
        "tag": "Placement",
        "meta": "Final Career Goal",
    })

    return steps
