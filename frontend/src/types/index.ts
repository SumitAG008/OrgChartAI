export interface Person {
  name: string;
  title?: string;
  avatar?: string;
  email?: string;
  employment_type?: string;
  position_type?: string;
  status?: string;
}

export interface TreeNode {
  id: string;
  person: Person;
  hasChild: boolean;
  hasParent: boolean;
  isHighlight: boolean;
  children?: TreeNode[];
}

export interface OrgChartResponse {
  tree: TreeNode;
  metadata?: Record<string, any>;
}
