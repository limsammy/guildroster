import React from 'react';
import { Card, Container } from '../ui';

const features = [
  {
    title: 'Attendance Tracking',
    description: 'Comprehensive raid attendance system with individual and bulk operations, filtering, and statistics.',
    icon: '📊',
    gradient: 'from-blue-500 to-cyan-500'
  },
  {
    title: 'Guild Management',
    description: 'Full CRUD operations for guilds, teams, and members with role-based access control.',
    icon: '⚔️',
    gradient: 'from-purple-500 to-pink-500'
  },
  {
    title: 'Raid Scheduling',
    description: 'Schedule and track raids with different difficulties, sizes, and team assignments.',
    icon: '🗓️',
    gradient: 'from-green-500 to-emerald-500'
  },
  {
    title: 'Character Profiles',
    description: 'Manage toons with class, role, main/alt designation, and team assignments.',
    icon: '👤',
    gradient: 'from-orange-500 to-red-500'
  },
  {
    title: 'Advanced Analytics',
    description: 'Streak tracking, attendance reports, and performance metrics with visual charts.',
    icon: '📈',
    gradient: 'from-indigo-500 to-purple-500'
  },
  {
    title: 'API Integration',
    description: 'RESTful API with automatic documentation, authentication, and comprehensive endpoints.',
    icon: '🔌',
    gradient: 'from-teal-500 to-blue-500'
  }
];

export const Features: React.FC = () => {
  return (
    <section className="py-20 bg-slate-900/50">
      <Container>
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-bold text-white mb-4">
            Forge Your Guild's Future
          </h2>
          <p className="text-xl text-slate-300 max-w-3xl mx-auto">
            Everything you need to lead your guild to victory, from attendance tracking to advanced analytics.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <Card key={index} variant="elevated" className="text-center group hover:scale-105 transition-transform duration-300">
              <div className={`w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r ${feature.gradient} flex items-center justify-center text-2xl group-hover:scale-110 transition-transform duration-300`}>
                {feature.icon}
              </div>
              <h3 className="text-xl font-semibold text-white mb-3">
                {feature.title}
              </h3>
              <p className="text-slate-300 leading-relaxed">
                {feature.description}
              </p>
            </Card>
          ))}
        </div>
      </Container>
    </section>
  );
}; 