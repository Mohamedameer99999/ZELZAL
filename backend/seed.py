from app import app
from database import db
from models import User, SecurityEvent, Project, Task, Activity, Conversation, AnalyticsEvent
from auth import create_user
from datetime import datetime, timedelta, timezone
import random

now = datetime.now(timezone.utc)

users_data = [
    {'username': 'admin', 'email': 'admin@zelzal.io', 'password': 'admin123', 'role': 'admin', 'bio': 'System administrator and security architect'},
    {'username': 'cyber_agent', 'email': 'agent@zelzal.io', 'password': 'agent123', 'role': 'analyst', 'bio': 'Senior security analyst'},
    {'username': 'netwatch', 'email': 'watch@zelzal.io', 'password': 'watch123', 'role': 'user', 'bio': 'Network security engineer'},
    {'username': 'shadowsilk', 'email': 'shadow@zelzal.io', 'password': 'shadow123', 'role': 'viewer', 'bio': 'External security auditor'},
    {'username': 'firewall_fox', 'email': 'fox@zelzal.io', 'password': 'fox123', 'role': 'user', 'bio': 'Penetration testing specialist'},
    {'username': 'zeroday', 'email': 'zero@zelzal.io', 'password': 'zero123', 'role': 'analyst', 'bio': 'Vulnerability researcher'},
    {'username': 'cipher_ghost', 'email': 'ghost@zelzal.io', 'password': 'ghost123', 'role': 'user', 'bio': 'Cryptography engineer'},
    {'username': 'darktrace', 'email': 'trace@zelzal.io', 'password': 'trace123', 'role': 'user', 'bio': 'Threat intelligence analyst'},
]

event_types = ['Brute Force Attack', 'Malware Detected', 'Unauthorized Access', 'Port Scan',
               'DNS Spoofing', 'SQL Injection', 'Phishing Attempt', 'DDoS Attack',
               'Man-in-the-Middle', 'Ransomware Detection', 'Zero-Day Exploit', 'Credential Stuffing']

severities = ['critical', 'high', 'medium', 'low']
statuses = ['active', 'investigating', 'resolved']

ips = ['192.168.1.105', '10.0.0.45', '203.0.113.50', '198.51.100.22', '192.0.2.77',
       '203.0.113.88', '172.16.0.33', '10.88.12.7', '192.168.45.120', '185.220.101.23']

project_templates = [
    {'name': 'Firewall Configuration', 'desc': 'Configure and deploy new firewall rules across all network segments', 'priority': 'high'},
    {'name': 'Penetration Testing', 'desc': 'Comprehensive security assessment of internal systems and infrastructure', 'priority': 'high'},
    {'name': 'Security Audit Q2', 'desc': 'Quarterly security audit and compliance check for all departments', 'priority': 'medium'},
    {'name': 'Incident Response Plan', 'desc': 'Develop and document incident response procedures and playbooks', 'priority': 'medium'},
    {'name': 'Network Monitoring Setup', 'desc': 'Deploy network monitoring agents across critical infrastructure', 'priority': 'low'},
    {'name': 'Vulnerability Assessment', 'desc': 'Scan and assess all internal and external systems for vulnerabilities', 'priority': 'high'},
    {'name': 'SIEM Implementation', 'desc': 'Deploy and configure Security Information and Event Management system', 'priority': 'medium'},
    {'name': 'Endpoint Protection', 'desc': 'Deploy next-gen endpoint protection across all workstations and servers', 'priority': 'high'},
]

task_templates = {
    'Firewall Configuration': ['Define rule sets', 'Test rule conflicts', 'Deploy to production', 'Verify deployment', 'Document changes'],
    'Penetration Testing': ['Reconnaissance phase', 'Vulnerability scanning', 'Exploitation testing', 'Report generation', 'Remediation plan'],
    'Security Audit Q2': ['Gather access logs', 'Review permissions', 'Check compliance', 'Generate audit report', 'Present findings'],
    'Incident Response Plan': ['Draft procedures', 'Review with team', 'Simulation testing', 'Finalize documentation', 'Train staff'],
    'Network Monitoring Setup': ['Select monitoring tools', 'Deploy agents', 'Configure alerts', 'Test monitoring', 'Dashboard setup'],
    'Vulnerability Assessment': ['Scope definition', 'Run scans', 'Analyze results', 'Prioritize findings', 'Create remediation plan'],
    'SIEM Implementation': ['Requirements gathering', 'Install SIEM', 'Configure log sources', 'Create correlation rules', 'Dashboard creation'],
    'Endpoint Protection': ['Vendor evaluation', 'Deploy agents', 'Configure policies', 'Test detection', 'Monitor performance'],
}

activity_actions = [
    ('System scan completed', 'No threats detected', 'security'),
    ('New user registered', 'New team member joined the platform', 'user'),
    ('Project updated', 'Project status changed', 'project'),
    ('Security alert resolved', 'Threat neutralized successfully', 'security'),
    ('AI analysis complete', 'Network pattern analysis finished', 'ai'),
    ('Backup completed', 'Daily backup was successful', 'system'),
    ('Threat intelligence update', 'New signatures added to database', 'security'),
    ('Performance optimization', 'System cache cleared', 'system'),
    ('Firewall rule updated', 'New rule deployed to production', 'security'),
    ('Report generated', 'Weekly security report ready', 'analytics'),
]

analytics_events = [
    ('page_view', 1.0), ('user_login', 1.0), ('threat_detected', 1.0),
    ('report_generated', 1.0), ('api_request', 1.0), ('scan_completed', 1.0),
]


def seed():
    with app.app_context():
        db.drop_all()
        db.create_all()

        users = []
        for ud in users_data:
            user = create_user(ud['username'], ud['email'], ud['password'], ud['role'])
            user.bio = ud['bio']
            db.session.add(user)
            users.append(user)
        db.session.flush()

        admin = users[0]

        for i in range(30):
            event = SecurityEvent(
                event_type=random.choice(event_types),
                severity=random.choice(severities),
                source_ip=random.choice(ips),
                description=f'{random.choice(event_types)} detected from {random.choice(ips)}',
                status=random.choice(statuses),
                created_at=now - timedelta(hours=random.randint(1, 720)),
            )
            db.session.add(event)

        for pt in project_templates:
            status = random.choice(['active', 'planning'])
            progress = random.randint(0, 100) if status == 'active' else random.randint(0, 20)
            project = Project(
                user_id=admin.id,
                name=pt['name'],
                description=pt['desc'],
                status=status,
                progress=progress,
                priority=pt['priority'],
                due_date=now + timedelta(days=random.randint(7, 60)),
                created_at=now - timedelta(days=random.randint(1, 90)),
            )
            db.session.add(project)
            db.session.flush()

            tasks = task_templates.get(pt['name'], ['Task 1', 'Task 2', 'Task 3'])
            task_statuses = ['done', 'in_progress', 'todo']
            for j, tname in enumerate(tasks):
                if j == 0 and progress > 0:
                    ts = 'done'
                elif j == len(tasks) - 1 and progress < 100:
                    ts = 'todo'
                else:
                    ts = random.choice(task_statuses)
                task = Task(
                    project_id=project.id,
                    title=tname,
                    status=ts,
                    assignee=random.choice(users).username if random.random() > 0.3 else '',
                    created_at=now - timedelta(days=random.randint(1, 30)),
                )
                db.session.add(task)

            actual_tasks = Task.query.filter(Task.project_id == project.id).all()
            done_count = sum(1 for t in actual_tasks if t.status == 'done')
            project.progress = round((done_count / len(actual_tasks)) * 100) if actual_tasks else 0

        for i in range(50):
            act = random.choice(activity_actions)
            activity = Activity(
                user_id=random.choice(users).id,
                action=act[0],
                details=act[1],
                category=act[2],
                created_at=now - timedelta(hours=random.randint(1, 720)),
            )
            db.session.add(activity)

        conv = Conversation(
            user_id=admin.id,
            title='Security Analysis Session',
            messages=[
                {'role': 'user', 'content': 'Check my system security', 'timestamp': (now - timedelta(hours=2)).isoformat()},
                {'role': 'assistant', 'content': 'I have analyzed your system. All critical parameters are within normal ranges. I recommend reviewing your active firewall rules.', 'timestamp': (now - timedelta(hours=2)).isoformat()},
                {'role': 'user', 'content': 'Any threats detected?', 'timestamp': (now - timedelta(hours=1)).isoformat()},
                {'role': 'assistant', 'content': 'No active threats detected. Your intrusion detection system is functioning optimally. Would you like me to run a deep scan?', 'timestamp': (now - timedelta(hours=1)).isoformat()},
            ],
        )
        db.session.add(conv)

        for i in range(100):
            ae = AnalyticsEvent(
                event_name=random.choice(analytics_events)[0],
                value=random.uniform(0.5, 100.0),
                metadata_json={'source': random.choice(['web', 'api', 'system']), 'user_id': random.choice(users).id},
                created_at=now - timedelta(hours=random.randint(1, 720)),
            )
            db.session.add(ae)

        db.session.commit()

        print(f'Seeded: {User.query.count()} users')
        print(f'Seeded: {SecurityEvent.query.count()} security events')
        print(f'Seeded: {Project.query.count()} projects')
        print(f'Seeded: {Task.query.count()} tasks')
        print(f'Seeded: {Activity.query.count()} activities')
        print(f'Seeded: {Conversation.query.count()} conversations')
        print(f'Seeded: {AnalyticsEvent.query.count()} analytics events')
        print('\nDatabase seeded successfully!')


if __name__ == '__main__':
    seed()
