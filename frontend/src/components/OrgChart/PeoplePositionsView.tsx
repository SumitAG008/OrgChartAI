import React, { useState } from 'react';
import { List, User, Users, Briefcase, Percent, Download, ChevronDown, FileText, Calendar } from 'lucide-react';

interface PositionData {
  id: string;
  positionTitle: string;
  person: string;
  manager: string;
  roles: string;
  accountabilities: string;
  membersOf: string;
  effort: number;
  startDate: string;
  endDate: string;
  isAIAgent?: boolean;
}

const PeoplePositionsView: React.FC = () => {
  const [sortBy, setSortBy] = useState('Person');
  const [showSortMenu, setShowSortMenu] = useState(false);

  // Sample data matching the provided structure
  const positionsData: PositionData[] = [
    { 
      id: '1', 
      positionTitle: 'Marketing Manager', 
      person: 'Margery Thomas', 
      manager: 'Brett Hans', 
      roles: 'Marketing Manager', 
      accountabilities: 'Brett Hans',
      membersOf: 'Brett Hans',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A' 
    },
    { 
      id: '2', 
      positionTitle: 'Chief Technology Officer', 
      person: 'Cly Mengue', 
      manager: 'Cly Mengue', 
      roles: 'Chief Technology Officer', 
      accountabilities: 'Georgeanne Gorke',
      membersOf: 'Georgeanne Gorke',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A' 
    },
    { 
      id: '3', 
      positionTitle: 'VP Engineering', 
      person: 'Cohen Kavanagh', 
      manager: 'Cohen Kavanagh', 
      roles: 'VP Engineering', 
      accountabilities: 'Cly Mengue',
      membersOf: 'Cly Mengue',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A' 
    },
    { 
      id: '4', 
      positionTitle: 'AI Market Analyst', 
      person: 'AI Agent "Sonny"', 
      manager: 'AI Agent "Sonny"', 
      roles: 'AI Market Analyst', 
      accountabilities: 'Brett Hans',
      membersOf: 'Brett Hans',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A',
      isAIAgent: true
    },
    { 
      id: '5', 
      positionTitle: 'Chief Executive Officer', 
      person: 'Georgeanne Gorke', 
      manager: 'Georgeanne Gorke', 
      roles: 'Chief Executive Officer', 
      accountabilities: 'N/A',
      membersOf: '',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A' 
    },
    { 
      id: '6', 
      positionTitle: 'Chief Marketing Officer', 
      person: 'Brett Hans', 
      manager: 'Brett Hans', 
      roles: 'Chief Marketing Officer', 
      accountabilities: 'Georgeanne Gorke',
      membersOf: 'Georgeanne Gorke',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A' 
    },
    { 
      id: '7', 
      positionTitle: 'AI Cross-Functional Integrator', 
      person: 'AI Agent "Eve"', 
      manager: 'AI Agent "Eve"', 
      roles: 'AI Cross-Functional In...', 
      accountabilities: 'Georgeanne Gorke',
      membersOf: 'Georgeanne Gorke',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A',
      isAIAgent: true
    },
    { 
      id: '8', 
      positionTitle: 'Chief Operating Officer', 
      person: 'Brita Lippitt', 
      manager: 'Brita Lippitt', 
      roles: 'Chief Operating Officer', 
      accountabilities: 'Georgeanne Gorke',
      membersOf: 'Georgeanne Gorke',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A' 
    },
    { 
      id: '9', 
      positionTitle: 'AI Chief Strategy Advisor', 
      person: 'AI Agent "Tars"', 
      manager: 'AI Agent "Tars"', 
      roles: 'AI Chief Strategy Advi...', 
      accountabilities: 'Georgeanne Gorke',
      membersOf: 'Georgeanne Gorke',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A',
      isAIAgent: true
    },
    { 
      id: '10', 
      positionTitle: 'Operations Director', 
      person: 'Teodor Enriquez', 
      manager: 'Teodor Enriquez', 
      roles: 'Operations Director', 
      accountabilities: 'Brita Lippitt',
      membersOf: 'Brita Lippitt',
      effort: 1, 
      startDate: 'N/A', 
      endDate: 'N/A' 
    },
  ];

  const sortOptions = [
    { label: 'Position ID', icon: '#' },
    { label: 'Position title', icon: '📋' },
    { label: 'Color', icon: '🎨' },
    { label: 'Person', icon: '👤' },
    { label: 'Name', icon: '👤' },
    { label: 'Email', icon: '@' },
    { label: 'Vacancy status', icon: '❓' },
    { label: 'Person ID', icon: '#' },
    { label: 'Manager', icon: '👥' },
    { label: 'Responsibilities', icon: '📄' },
    { label: 'Total compensation', icon: '$' },
  ];

  const getInitials = (name: string) => {
    if (name.includes('AI Agent')) {
      return 'A';
    }
    const parts = name.split(' ');
    if (parts.length >= 2) {
      return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
    }
    return name.substring(0, 2).toUpperCase();
  };

  const getPersonColor = (name: string, isAIAgent?: boolean) => {
    if (isAIAgent) {
      return 'from-purple-500 to-purple-600';
    }
    // Generate consistent color based on name
    const colors = [
      'from-blue-400 to-blue-600',
      'from-green-400 to-green-600',
      'from-orange-400 to-orange-600',
      'from-pink-400 to-pink-600',
      'from-indigo-400 to-indigo-600',
      'from-teal-400 to-teal-600',
    ];
    const index = name.charCodeAt(0) % colors.length;
    return colors[index];
  };

  return (
    <div className="flex-1 flex flex-col overflow-hidden bg-white">
      {/* Toolbar */}
      <div className="bg-white border-b border-gray-200 px-5 py-3 flex items-center gap-3">
        <button className="flex items-center gap-2 px-3 py-1.5 text-sm text-black border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold">
          <List size={16} className="text-black" />
          Properties
        </button>
        <button className="flex items-center gap-2 px-3 py-1.5 text-sm text-black border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold">
          Group
        </button>
        <button className="flex items-center gap-2 px-3 py-1.5 text-sm text-black border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold">
          Filter
        </button>
        <div className="relative">
          <button 
            onClick={() => setShowSortMenu(!showSortMenu)}
            className="flex items-center gap-2 px-3 py-1.5 text-sm text-black border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold bg-gray-50"
          >
            Sort: {sortBy} ↑
            <ChevronDown size={14} className="text-black" />
          </button>
          {showSortMenu && (
            <div className="absolute top-full left-0 mt-1 w-56 bg-white rounded-lg shadow-xl border border-gray-200 py-1 z-50 max-h-96 overflow-y-auto">
              {sortOptions.map((option) => (
                <button
                  key={option.label}
                  onClick={() => {
                    setSortBy(option.label);
                    setShowSortMenu(false);
                  }}
                  className="w-full px-4 py-2 text-left text-sm text-black hover:bg-gray-100 flex items-center gap-2 font-semibold"
                >
                  <span className="text-xs">{option.icon}</span>
                  {option.label}
                  {sortBy === option.label && (
                    <span className="ml-auto text-green-600">✓</span>
                  )}
                </button>
              ))}
            </div>
          )}
        </div>
        <button className="flex items-center gap-2 px-3 py-1.5 text-sm text-black border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors font-semibold">
          <Download size={16} className="text-black" />
          Import / update
        </button>
      </div>

      {/* Table */}
      <div className="flex-1 overflow-auto">
        <table className="w-full border-collapse text-sm">
          <thead className="bg-gray-50 sticky top-0 z-10">
            <tr>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <List size={16} className="text-black" />
                  Position title
                </div>
              </th>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <User size={16} className="text-black" />
                  Person
                </div>
              </th>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <Users size={16} className="text-black" />
                  Manager
                </div>
              </th>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <Briefcase size={16} className="text-black" />
                  Roles
                </div>
              </th>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <FileText size={16} className="text-black" />
                  Accountabilities
                </div>
              </th>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <Users size={16} className="text-black" />
                  Members of
                </div>
              </th>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <Percent size={16} className="text-black" />
                  Effort (FTE)
                </div>
              </th>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <Calendar size={16} className="text-black" />
                  Start date
                </div>
              </th>
              <th className="px-4 py-3 text-left font-bold text-black border-b border-gray-200">
                <div className="flex items-center gap-2">
                  <Calendar size={16} className="text-black" />
                  End date
                </div>
              </th>
            </tr>
          </thead>
          <tbody>
            {positionsData.map((position) => (
              <tr 
                key={position.id} 
                className={`hover:bg-gray-50 border-b border-gray-100 ${position.isAIAgent ? 'bg-purple-50/30' : ''}`}
              >
                <td className="px-4 py-3">
                  <div className="flex items-center gap-3">
                    {position.isAIAgent ? (
                      <div className="w-1 h-6 bg-purple-500 rounded" />
                    ) : (
                      <div className="w-1 h-6 bg-blue-500 rounded" />
                    )}
                    <span className="font-semibold text-black">{position.positionTitle}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className={`w-8 h-8 bg-gradient-to-br ${getPersonColor(position.person, position.isAIAgent)} rounded-full flex items-center justify-center text-white text-xs font-bold`}>
                      {getInitials(position.person)}
                    </div>
                    <span className="text-black font-semibold">{position.person}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <div className={`w-8 h-8 bg-gradient-to-br ${getPersonColor(position.manager, position.manager.includes('AI Agent'))} rounded-full flex items-center justify-center text-white text-xs font-bold`}>
                      {getInitials(position.manager)}
                    </div>
                    <span className="text-black font-semibold">{position.manager}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="inline-flex items-center gap-2 px-3 py-1 bg-gray-100 rounded-lg text-xs">
                    <Briefcase size={14} className="text-black" />
                    <span className="text-black font-semibold">{position.roles}</span>
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-black font-semibold">{position.accountabilities}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-black font-semibold">{position.membersOf || '-'}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-black font-semibold">{position.effort}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-black font-semibold">{position.startDate}</span>
                </td>
                <td className="px-4 py-3">
                  <span className="text-black font-semibold">{position.endDate}</span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="px-4 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between">
          <div className="text-sm text-black font-bold">
            <strong>Sum {positionsData.length}</strong>
          </div>
          <button className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-semibold flex items-center gap-2">
            <Briefcase size={16} />
            Add position
          </button>
        </div>
      </div>
    </div>
  );
};

export default PeoplePositionsView;
