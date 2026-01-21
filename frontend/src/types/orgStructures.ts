/**
 * All 26 Organizational Structure Types
 * Complete type definitions for visualization system
 */

export type OrgStructureType =
  // Hierarchical Structures (6 types)
  | 'classic-top-down'
  | 'bottom-up'
  | 'vertical-functional'
  | 'horizontal-functional'
  | 'multi-layered'
  | 'span-of-control'
  // Divisional Structures (4 types)
  | 'product-divisional'
  | 'geography-divisional'
  | 'market-segment'
  | 'multi-divisional'
  // Matrix Structures (3 types)
  | 'matrix-2x2'
  | 'matrix-3axis'
  | 'cross-functional-matrix'
  // Network & Modern (5 types)
  | 'network'
  | 'holacracy'
  | 'pod-based'
  | 'agile-squad'
  | 'ecosystem'
  // Radial & Circular (3 types)
  | 'radial-hub-spoke'
  | 'concentric-circles'
  | 'circular-relationship'
  // Flow-Based (3 types)
  | 'process-flow'
  | 'value-stream'
  | 'decision-flow'
  // Hybrid (2 types)
  | 'hybrid-hierarchy-matrix'
  | 'hybrid-divisional-network';

export interface OrgStructureConfig {
  id: OrgStructureType;
  name: string;
  category: string;
  description: string;
  icon: string;
  layout: 'hierarchical' | 'radial' | 'matrix' | 'network' | 'flow' | 'hybrid';
  features: string[];
}

export const ORG_STRUCTURE_TYPES: Record<OrgStructureType, OrgStructureConfig> = {
  // Hierarchical Structures
  'classic-top-down': {
    id: 'classic-top-down',
    name: 'Classic Top-Down Hierarchy',
    category: 'Hierarchical',
    description: 'Traditional pyramid structure with CEO at top, cascading down',
    icon: '📊',
    layout: 'hierarchical',
    features: ['Traditional', 'Clear hierarchy', 'Most common']
  },
  'bottom-up': {
    id: 'bottom-up',
    name: 'Bottom-Up Hierarchy',
    category: 'Hierarchical',
    description: 'Inverted pyramid with front-line employees at top',
    icon: '⬆️',
    layout: 'hierarchical',
    features: ['Inverted', 'Employee-focused', 'Modern approach']
  },
  'vertical-functional': {
    id: 'vertical-functional',
    name: 'Vertical Functional Structure',
    category: 'Hierarchical',
    description: 'Organized by function (HR, Finance, Engineering) in vertical columns',
    icon: '📋',
    layout: 'hierarchical',
    features: ['Function-based', 'Vertical columns', 'Clear boundaries']
  },
  'horizontal-functional': {
    id: 'horizontal-functional',
    name: 'Horizontal Functional Structure',
    category: 'Hierarchical',
    description: 'Functions arranged horizontally with cross-functional collaboration',
    icon: '↔️',
    layout: 'hierarchical',
    features: ['Horizontal', 'Cross-functional', 'Flat structure']
  },
  'multi-layered': {
    id: 'multi-layered',
    name: 'Multi-Layered Hierarchy',
    category: 'Hierarchical',
    description: 'Multiple hierarchy levels with expandable/collapsible layers',
    icon: '📚',
    layout: 'hierarchical',
    features: ['Deep depth', 'Expandable', 'Layered view']
  },
  'span-of-control': {
    id: 'span-of-control',
    name: 'Span-of-Control Chart',
    category: 'Hierarchical',
    description: 'Focus on manager-to-direct-report ratios and management efficiency',
    icon: '🎯',
    layout: 'hierarchical',
    features: ['Management focus', 'Ratio visualization', 'Efficiency metrics']
  },
  // Divisional Structures
  'product-divisional': {
    id: 'product-divisional',
    name: 'Product-Based Divisional',
    category: 'Divisional',
    description: 'Organized by product lines with independent product teams',
    icon: '📦',
    layout: 'hierarchical',
    features: ['Product-focused', 'Independent teams', 'Product lines']
  },
  'geography-divisional': {
    id: 'geography-divisional',
    name: 'Geography-Based Divisional',
    category: 'Divisional',
    description: 'Organized by geographic regions with regional autonomy',
    icon: '🌍',
    layout: 'hierarchical',
    features: ['Regional', 'Geographic', 'Location-based']
  },
  'market-segment': {
    id: 'market-segment',
    name: 'Market/Customer Segment Structure',
    category: 'Divisional',
    description: 'Organized by customer segments with market-focused divisions',
    icon: '👥',
    layout: 'hierarchical',
    features: ['Customer-focused', 'Market segments', 'Customer-centric']
  },
  'multi-divisional': {
    id: 'multi-divisional',
    name: 'Multi-Divisional (M-Form)',
    category: 'Divisional',
    description: 'Multiple divisions with central HQ, each operating semi-independently',
    icon: '🏢',
    layout: 'hierarchical',
    features: ['Multiple divisions', 'Central HQ', 'Semi-independent']
  },
  // Matrix Structures
  'matrix-2x2': {
    id: 'matrix-2x2',
    name: '2×2 Matrix (Dual Reporting)',
    category: 'Matrix',
    description: 'Dual reporting lines with functional and project managers',
    icon: '⚡',
    layout: 'matrix',
    features: ['Dual reporting', 'Cross-functional', 'Collaborative']
  },
  'matrix-3axis': {
    id: 'matrix-3axis',
    name: '3-Axis Matrix (Role × Region × Product)',
    category: 'Matrix',
    description: 'Three-dimensional matrix with complex reporting relationships',
    icon: '🔷',
    layout: 'matrix',
    features: ['3D matrix', 'Complex relationships', 'Multi-dimensional']
  },
  'cross-functional-matrix': {
    id: 'cross-functional-matrix',
    name: 'Cross-Functional Matrix',
    category: 'Matrix',
    description: 'Functional departments × project teams with shared resources',
    icon: '🔀',
    layout: 'matrix',
    features: ['Cross-functional', 'Shared resources', 'Project teams']
  },
  // Network & Modern
  'network': {
    id: 'network',
    name: 'Network Organization',
    category: 'Network & Modern',
    description: 'Interconnected nodes with no strict hierarchy, relationship-based',
    icon: '🕸️',
    layout: 'network',
    features: ['Interconnected', 'No hierarchy', 'Relationship-based']
  },
  'holacracy': {
    id: 'holacracy',
    name: 'Holacracy / Circle Structure',
    category: 'Network & Modern',
    description: 'Circular organizational units with self-organizing teams',
    icon: '⭕',
    layout: 'network',
    features: ['Circular', 'Self-organizing', 'Distributed authority']
  },
  'pod-based': {
    id: 'pod-based',
    name: 'Pod-Based Structure',
    category: 'Network & Modern',
    description: 'Small autonomous teams (pods) with pod-to-pod relationships',
    icon: '🫧',
    layout: 'network',
    features: ['Autonomous pods', 'Agile', 'Small teams']
  },
  'agile-squad': {
    id: 'agile-squad',
    name: 'Agile Squad/Tribe Structure',
    category: 'Network & Modern',
    description: 'Squads (small teams), Tribes (collections), Guilds (communities)',
    icon: '🚀',
    layout: 'network',
    features: ['Squads', 'Tribes', 'Guilds', 'Agile']
  },
  'ecosystem': {
    id: 'ecosystem',
    name: 'Ecosystem Structure',
    category: 'Network & Modern',
    description: 'Partner and vendor relationships with external connections',
    icon: '🌐',
    layout: 'network',
    features: ['Partners', 'Vendors', 'External', 'Extended org']
  },
  // Radial & Circular
  'radial-hub-spoke': {
    id: 'radial-hub-spoke',
    name: 'Radial Hub-and-Spoke',
    category: 'Radial & Circular',
    description: 'Central hub with radiating spokes, central leadership',
    icon: '☀️',
    layout: 'radial',
    features: ['Central hub', 'Radiating spokes', 'Centralized']
  },
  'concentric-circles': {
    id: 'concentric-circles',
    name: 'Concentric Circle Structure',
    category: 'Radial & Circular',
    description: 'Multiple concentric circles with inner leadership, outer organization',
    icon: '🎯',
    layout: 'radial',
    features: ['Concentric', 'Inner leadership', 'Outer org']
  },
  'circular-relationship': {
    id: 'circular-relationship',
    name: 'Circular Team Relationship Map',
    category: 'Radial & Circular',
    description: 'Circular arrangement focused on relationships and collaboration',
    icon: '🔄',
    layout: 'radial',
    features: ['Circular', 'Relationship-focused', 'Collaboration']
  },
  // Flow-Based
  'process-flow': {
    id: 'process-flow',
    name: 'Process-Flow Org Structure',
    category: 'Flow-Based',
    description: 'Organized by business processes with process-driven hierarchy',
    icon: '🌊',
    layout: 'flow',
    features: ['Process-driven', 'Workflow', 'Business processes']
  },
  'value-stream': {
    id: 'value-stream',
    name: 'Value-Stream Org Structure',
    category: 'Flow-Based',
    description: 'Organized by value streams with value delivery focus',
    icon: '💎',
    layout: 'flow',
    features: ['Value streams', 'Value delivery', 'Customer value']
  },
  'decision-flow': {
    id: 'decision-flow',
    name: 'Decision-Flow Org Structure',
    category: 'Flow-Based',
    description: 'Organized by decision-making authority with decision rights visualization',
    icon: '⚖️',
    layout: 'flow',
    features: ['Decision rights', 'Authority flow', 'Decision-making']
  },
  // Hybrid
  'hybrid-hierarchy-matrix': {
    id: 'hybrid-hierarchy-matrix',
    name: 'Hybrid Hierarchy + Matrix',
    category: 'Hybrid & Custom',
    description: 'Combines hierarchical and matrix elements with flexible structure',
    icon: '🔀',
    layout: 'hybrid',
    features: ['Hybrid', 'Flexible', 'Dual reporting']
  },
  'hybrid-divisional-network': {
    id: 'hybrid-divisional-network',
    name: 'Hybrid Divisional + Network',
    category: 'Hybrid & Custom',
    description: 'Divisional structure with network elements and cross-divisional collaboration',
    icon: '🌉',
    layout: 'hybrid',
    features: ['Divisional', 'Network', 'Cross-divisional']
  }
};

export const STRUCTURE_CATEGORIES = [
  'Hierarchical',
  'Divisional',
  'Matrix',
  'Network & Modern',
  'Radial & Circular',
  'Flow-Based',
  'Hybrid & Custom'
] as const;
