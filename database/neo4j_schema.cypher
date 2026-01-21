// Neo4j Graph Database Schema
// OrgChartAI - Graph Relationships and Constraints

// ============================================
// CONSTRAINTS
// ============================================

// Create constraints for unique properties
CREATE CONSTRAINT org_unit_id IF NOT EXISTS
FOR (o:OrgUnit) REQUIRE o.id IS UNIQUE;

CREATE CONSTRAINT position_id IF NOT EXISTS
FOR (p:Position) REQUIRE p.id IS UNIQUE;

CREATE CONSTRAINT employee_id IF NOT EXISTS
FOR (e:Employee) REQUIRE e.id IS UNIQUE;

CREATE CONSTRAINT job_id IF NOT EXISTS
FOR (j:Job) REQUIRE j.id IS UNIQUE;

CREATE CONSTRAINT skill_id IF NOT EXISTS
FOR (s:Skill) REQUIRE s.id IS UNIQUE;

// ============================================
// INDEXES
// ============================================

CREATE INDEX org_unit_code IF NOT EXISTS
FOR (o:OrgUnit) ON (o.code);

CREATE INDEX position_code IF NOT EXISTS
FOR (p:Position) ON (p.position_code);

CREATE INDEX employee_number IF NOT EXISTS
FOR (e:Employee) ON (e.employee_number);

CREATE INDEX skill_code IF NOT EXISTS
FOR (s:Skill) ON (s.code);

// ============================================
// RELATIONSHIP TYPES
// ============================================

// Org Unit Hierarchy
// (OrgUnit)-[:PARENT_OF]->(OrgUnit)
// (OrgUnit)-[:CONTAINS]->(Position)

// Position Relationships
// (Position)-[:REPORTS_TO]->(Position)
// (Position)-[:BELONGS_TO]->(OrgUnit)
// (Position)-[:HAS_JOB_PROFILE]->(Job)

// Employee Relationships
// (Employee)-[:OCCUPIES]->(Position)
// (Employee)-[:HAS_SKILL]->(Skill)
// (Employee)-[:MANAGES]->(Position)

// Assignment Relationships
// (Employee)-[:ASSIGNED_TO {type, start_date, end_date}]->(Position)
// (Employee)-[:TEMPORARY_ASSIGNMENT {start_date, end_date}]->(Position)

// Skill Relationships
// (Job)-[:REQUIRES_SKILL {level, mandatory}]->(Skill)
// (Position)-[:REQUIRES_SKILL {level, mandatory}]->(Skill)
// (Employee)-[:HAS_SKILL {level, validated}]->(Skill)

// Scenario Relationships
// (Scenario)-[:CONTAINS]->(OrgUnit)
// (Scenario)-[:CONTAINS]->(Position)

// ============================================
// SAMPLE QUERIES
// ============================================

// Get org hierarchy
// MATCH (root:OrgUnit {code: 'ROOT'})
// CALL apoc.path.subgraphNodes(root, {
//   relationshipFilter: 'PARENT_OF>',
//   labelFilter: '+OrgUnit'
// })
// YIELD node
// RETURN node

// Get reporting chain
// MATCH path = (p:Position)-[:REPORTS_TO*]->(manager:Position {id: $manager_id})
// RETURN path

// Find employees with skills
// MATCH (e:Employee)-[:HAS_SKILL]->(s:Skill {code: $skill_code})
// WHERE e.status = 'Active'
// RETURN e, s

// Get team composition
// MATCH (manager:Position {id: $manager_id})
// MATCH (employee:Employee)-[:OCCUPIES]->(position:Position)-[:REPORTS_TO]->(manager)
// RETURN employee, position
