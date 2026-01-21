import React from 'react';
import { motion } from 'framer-motion';
import { User, Briefcase, Mail, Building2 } from 'lucide-react';
import { TreeNode } from '../../types';

import { DisplayProperties } from './PropertiesPanel';

interface OrgNodeProps {
  node: TreeNode;
  onClick?: () => void;
  onHover?: (hovered: boolean) => void;
  isSelected?: boolean;
  isHovered?: boolean;
  displayProperties?: DisplayProperties;
}

const OrgNode: React.FC<OrgNodeProps> = ({
  node,
  onClick,
  onHover,
  isSelected = false,
  isHovered = false,
  displayProperties
}) => {
  // Default display properties if not provided
  const props = displayProperties || {
    personPhoto: true,
    personName: true,
    title: true,
    description: false,
    positionId: false,
    fte: false,
    vacancyStatus: false,
    totalCompensation: false,
    groupDescription: false,
    comments: true,
    roleEffortPercent: true,
  };
  const person = node.person;
  const isAI = person.position_type === 'AI Agent' || person.name?.includes('AI Agent') || person.title?.includes('AI');

  return (
    <motion.div
      initial={{ scale: 0.9, opacity: 0 }}
      animate={{ 
        scale: isHovered ? 1.02 : isSelected ? 1.01 : 1,
        opacity: 1
      }}
      whileHover={{ scale: 1.02 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      onMouseEnter={() => onHover?.(true)}
      onMouseLeave={() => onHover?.(false)}
      className={`
        relative w-[220px] bg-white rounded-xl border-2 transition-all duration-300 cursor-pointer
        shadow-sm hover:shadow-lg
        ${isSelected 
          ? 'border-purple-500 shadow-lg shadow-purple-500/20' 
          : isAI
          ? 'border-purple-500 hover:border-purple-600'
          : 'border-gray-200 hover:border-gray-300'
        }
      `}
    >
      {/* Gradient Background for AI Agents */}
      {isAI && (
        <div className="absolute inset-0 bg-gradient-to-br from-purple-50/50 to-purple-50/30 rounded-xl pointer-events-none" />
      )}

      {/* Header */}
      <div className="p-4 pb-3 relative z-10">
        <div className="flex items-start gap-3">
          {/* Avatar */}
          <div className={`
            w-12 h-12 rounded-full flex items-center justify-center text-white font-semibold text-lg flex-shrink-0
            ${isAI 
              ? 'bg-gradient-to-br from-purple-500 to-purple-600 ring-2 ring-purple-300' 
              : 'bg-gradient-to-br from-indigo-500 to-purple-600'
            }
          `} style={person.avatar && !isAI ? { backgroundImage: `url(${person.avatar})`, backgroundSize: 'cover' } : {}}>
            {!person.avatar && (
              isAI ? (
                <span className="text-2xl">🤖</span>
              ) : (
                <User className="w-6 h-6" />
              )
            )}
          </div>

          {/* Name and Title */}
          <div className="flex-1 min-w-0">
            {isAI ? (
              <>
                <div className="flex items-center gap-1.5 mb-1">
                  <span className="text-xs font-semibold text-purple-700">AI Agent</span>
                  {person.name && (
                    <span className="text-xs font-semibold text-purple-700">'{person.name.replace('AI Agent ', '').replace("'", '')}'</span>
                  )}
                </div>
                {props.title && (
                  <h3 className="font-semibold text-gray-900 text-sm truncate leading-tight">
                    {person.title || person.name}
                  </h3>
                )}
              </>
            ) : (
              <>
                {props.personName && (
                  <h3 className="font-semibold text-gray-900 text-sm truncate leading-tight">
                    {person.name}
                  </h3>
                )}
                {props.title && person.title && (
                  <p className="text-xs text-gray-600 truncate mt-0.5 leading-tight">
                    {person.title}
                  </p>
                )}
              </>
            )}
          </div>

          {/* AI Badge - Purple Circle with 'A' */}
          {isAI && (
            <div className="w-8 h-8 bg-gradient-to-br from-purple-500 to-purple-600 rounded-full flex items-center justify-center shadow-lg flex-shrink-0 absolute -top-2 -right-2">
              <span className="text-white font-bold text-sm">A</span>
            </div>
          )}
        </div>
      </div>

      {/* Divider */}
      <div className="h-px bg-gray-100 mx-4" />

      {/* Details */}
      <div className="p-3 pt-2 space-y-1.5 relative z-10">
        {/* Role/Position */}
        <div className="flex items-center gap-2 text-xs text-gray-600">
          <Briefcase className="w-3 h-3 flex-shrink-0" />
          <span className="truncate">{person.title || 'Position'}</span>
        </div>

        {/* Email */}
        {person.email && (
          <div className="flex items-center gap-2 text-xs text-gray-600">
            <Mail className="w-3 h-3 flex-shrink-0" />
            <span className="truncate">{person.email}</span>
          </div>
        )}
        
        {/* Employment Type */}
        {person.employment_type && (
          <div className="flex items-center justify-between pt-1">
            <span className="text-xs text-gray-500">Type:</span>
            <span className={`
              text-xs px-2 py-0.5 rounded-full font-medium
              ${isAI 
                ? 'bg-purple-100 text-purple-700' 
                : person.employment_type === 'Permanent'
                ? 'bg-blue-100 text-blue-700'
                : 'bg-gray-100 text-gray-700'
              }
            `}>
              {person.employment_type}
            </span>
          </div>
        )}

        {/* Status */}
        {person.status && (
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-500">Status:</span>
            <span className={`
              text-xs px-2 py-0.5 rounded-full font-medium
              ${person.status === 'Active' 
                ? 'bg-green-100 text-green-700' 
                : person.status === 'Vacant'
                ? 'bg-yellow-100 text-yellow-700'
                : 'bg-gray-100 text-gray-700'
              }
            `}>
              {person.status}
            </span>
          </div>
        )}
      </div>

      {/* Children Indicator */}
      {node.hasChild && node.children && node.children.length > 0 && (
        <div className="absolute -bottom-2 left-1/2 transform -translate-x-1/2 z-20">
          <div className="w-8 h-8 bg-gradient-to-r from-green-600 to-emerald-600 rounded-full flex items-center justify-center text-white text-xs font-bold shadow-lg shadow-green-500/50">
            {node.children.length}
          </div>
        </div>
      )}

      {/* Selection Indicator */}
      {isSelected && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className={`absolute -inset-1 border-2 rounded-xl pointer-events-none ${
            isAI ? 'border-purple-500' : 'border-green-500'
          }`}
        />
      )}
    </motion.div>
  );
};

export default OrgNode;
