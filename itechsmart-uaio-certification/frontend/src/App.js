import React, { useState, useEffect } from 'react';
import './App.css';

const iTechSmartUAIOCertification = () => {
  const [activeFilter, setActiveFilter] = useState('all');
  const [userProgress, setUserProgress] = useState({
    completedCourses: 3,
    totalCourses: 8,
    currentLevel: 'Associate',
    totalXP: 1250,
    nextLevelXP: 2000,
    certificationPath: 'UAIO Architect'
  });

  const [courses] = useState([
    {
      id: 1,
      title: 'Introduction to Autonomous Systems',
      level: 'Beginner',
      status: 'completed',
      progress: 100,
      duration: '4 weeks',
      modules: 12,
      description: 'Learn the fundamentals of autonomous systems and AI governance',
      xp: 200
    },
    {
      id: 2,
      title: 'AI Safety and Ethics',
      level: 'Beginner',
      status: 'completed',
      progress: 100,
      duration: '3 weeks',
      modules: 10,
      description: 'Understanding ethical considerations in AI development',
      xp: 180
    },
    {
      id: 3,
      title: 'Digital Twin Fundamentals',
      level: 'Intermediate',
      status: 'completed',
      progress: 100,
      duration: '5 weeks',
      modules: 15,
      description: 'Building and managing digital twin systems',
      xp: 250
    },
    {
      id: 4,
      title: 'Generative Workflow Design',
      level: 'Intermediate',
      status: 'in-progress',
      progress: 65,
      duration: '6 weeks',
      modules: 18,
      description: 'Creating automated workflows with AI assistance',
      xp: 300
    },
    {
      id: 5,
      title: 'Predictive Analytics',
      level: 'Intermediate',
      status: 'in-progress',
      progress: 30,
      duration: '5 weeks',
      modules: 14,
      description: 'Advanced analytics and prediction modeling',
      xp: 220
    },
    {
      id: 6,
      title: 'Enterprise Architecture',
      level: 'Advanced',
      status: 'not-started',
      progress: 0,
      duration: '8 weeks',
      modules: 24,
      description: 'Designing scalable enterprise systems',
      xp: 400
    },
    {
      id: 7,
      title: 'Multi-Cloud Orchestration',
      level: 'Advanced',
      status: 'not-started',
      progress: 0,
      duration: '7 weeks',
      modules: 21,
      description: 'Managing applications across multiple cloud providers',
      xp: 350
    },
    {
      id: 8,
      title: 'Capstone Project',
      level: 'Expert',
      status: 'not-started',
      progress: 0,
      duration: '10 weeks',
      modules: 30,
      description: 'Complete end-to-end UAIO system implementation',
      xp: 500
    }
  ]);

  const [achievements] = useState([
    {
      id: 1,
      title: 'First Steps',
      description: 'Complete your first course',
      icon: '🎯',
      unlocked: true,
      unlockedDate: '2024-01-15'
    },
    {
      id: 2,
      title: 'Quick Learner',
      description: 'Complete 3 courses in one month',
      icon: '⚡',
      unlocked: true,
      unlockedDate: '2024-02-01'
    },
    {
      id: 3,
      title: 'Knowledge Seeker',
      description: 'Complete 5 courses',
      icon: '📚',
      unlocked: false
    },
    {
      id: 4,
      title: 'Master Architect',
      description: 'Complete all courses',
      icon: '🏆',
      unlocked: false
    },
    {
      id: 5,
      title: 'Perfect Score',
      description: 'Score 100% on any course',
      icon: '💯',
      unlocked: true,
      unlockedDate: '2024-01-28'
    },
    {
      id: 6,
      title: 'Streak Master',
      description: 'Study for 30 consecutive days',
      icon: '🔥',
      unlocked: false
    }
  ]);

  const [activeNav, setActiveNav] = useState('dashboard');

  useEffect(() => {
    // Calculate progress
    const completed = courses.filter(course => course.status === 'completed').length;
    const inProgress = courses.filter(course => course.status === 'in-progress').length;
    const overallProgress = (completed / courses.length) * 100;
    
    setUserProgress(prev => ({
      ...prev,
      completedCourses: completed,
      overallProgress: overallProgress
    }));
  }, [courses]);

  const filteredCourses = courses.filter(course => {
    if (activeFilter === 'all') return true;
    if (activeFilter === 'in-progress') return course.status === 'in-progress';
    if (activeFilter === 'completed') return course.status === 'completed';
    if (activeFilter === 'not-started') return course.status === 'not-started';
    return true;
  });

  const getLevelColor = (level) => {
    switch (level) {
      case 'Beginner': return '#4facfe';
      case 'Intermediate': return '#f093fb';
      case 'Advanced': return '#f5576c';
      case 'Expert': return '#38ef7d';
      default: return '#6b7280';
    }
  };

  const getStatusClass = (status) => {
    switch (status) {
      case 'completed': return 'completed';
      case 'in-progress': return 'in-progress';
      case 'not-started': return 'not-started';
      default: return 'not-started';
    }
  };

  const getProgressColor = (progress) => {
    if (progress === 100) return '#38ef7d';
    if (progress >= 50) return '#4facfe';
    if (progress > 0) return '#f093fb';
    return '#6b7280';
  };

  return (
    <div className="certification-app">
      {/* Header */}
      <header className="header">
        <div className="header-content">
          <div className="logo-section">
            <div className="logo-icon">🎓</div>
            <div className="logo-text">UAIO Architect Certification</div>
          </div>
          <div className="user-profile">
            <div className="user-avatar">JD</div>
            <div className="user-info">
              <div className="user-name">John Doe</div>
              <div className="user-level">{userProgress.currentLevel}</div>
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="main-content">
        {/* Sidebar Navigation */}
        <aside className="sidebar">
          <div className="sidebar-header">Navigation</div>
          <nav>
            <ul className="nav-menu">
              <li className="nav-item">
                <a 
                  href="#dashboard" 
                  className={`nav-link ${activeNav === 'dashboard' ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveNav('dashboard');
                  }}
                >
                  <span className="nav-icon">📊</span>
                  Dashboard
                </a>
              </li>
              <li className="nav-item">
                <a 
                  href="#courses" 
                  className={`nav-link ${activeNav === 'courses' ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveNav('courses');
                  }}
                >
                  <span className="nav-icon">📚</span>
                  Courses
                </a>
              </li>
              <li className="nav-item">
                <a 
                  href="#achievements" 
                  className={`nav-link ${activeNav === 'achievements' ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveNav('achievements');
                  }}
                >
                  <span className="nav-icon">🏆</span>
                  Achievements
                </a>
              </li>
              <li className="nav-item">
                <a 
                  href="#certificates" 
                  className={`nav-link ${activeNav === 'certificates' ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveNav('certificates');
                  }}
                >
                  <span className="nav-icon">📜</span>
                  Certificates
                </a>
              </li>
              <li className="nav-item">
                <a 
                  href="#community" 
                  className={`nav-link ${activeNav === 'community' ? 'active' : ''}`}
                  onClick={(e) => {
                    e.preventDefault();
                    setActiveNav('community');
                  }}
                >
                  <span className="nav-icon">👥</span>
                  Community
                </a>
              </li>
            </ul>
          </nav>
        </aside>

        {/* Content Area */}
        <div className="content-area">
          {/* Progress Overview */}
          <div className="progress-overview fade-in">
            <div className="progress-header">
              <h1 className="progress-title">Your Learning Journey</h1>
              <div className="progress-stats">
                <div className="stat-item">
                  <div className="stat-value">{userProgress.completedCourses}/{userProgress.totalCourses}</div>
                  <div className="stat-label">Courses</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{userProgress.totalXP} XP</div>
                  <div className="stat-label">Total Points</div>
                </div>
                <div className="stat-item">
                  <div className="stat-value">{userProgress.currentLevel}</div>
                  <div className="stat-label">Current Level</div>
                </div>
              </div>
            </div>
            
            <div className="overall-progress">
              <div className="progress-bar-container">
                <div 
                  className="progress-bar"
                  style={{ 
                    width: `${(userProgress.completedCourses / userProgress.totalCourses) * 100}%`,
                    background: `linear-gradient(90deg, #667eea, #764ba2)`
                  }}
                />
              </div>
              <div className="progress-details">
                <span>Overall Progress</span>
                <span>{Math.round((userProgress.completedCourses / userProgress.totalCourses) * 100)}%</span>
              </div>
            </div>
          </div>

          {/* Courses Section */}
          <div className="courses-section fade-in">
            <div className="section-header">
              <h2 className="section-title">Available Courses</h2>
              <div className="filter-buttons">
                <button 
                  className={`filter-button ${activeFilter === 'all' ? 'active' : ''}`}
                  onClick={() => setActiveFilter('all')}
                >
                  All Courses
                </button>
                <button 
                  className={`filter-button ${activeFilter === 'in-progress' ? 'active' : ''}`}
                  onClick={() => setActiveFilter('in-progress')}
                >
                  In Progress
                </button>
                <button 
                  className={`filter-button ${activeFilter === 'completed' ? 'active' : ''}`}
                  onClick={() => setActiveFilter('completed')}
                >
                  Completed
                </button>
                <button 
                  className={`filter-button ${activeFilter === 'not-started' ? 'active' : ''}`}
                  onClick={() => setActiveFilter('not-started')}
                >
                  Not Started
                </button>
              </div>
            </div>
            
            <div className="courses-grid">
              {filteredCourses.map(course => (
                <div key={course.id} className="course-card">
                  <div className={`course-status ${getStatusClass(course.status)}`}>
                    {course.status.replace('-', ' ')}
                  </div>
                  
                  <div className="course-header">
                    <div className="course-title">{course.title}</div>
                    <div className="course-level">
                      <span className="level-badge" style={{ background: getLevelColor(course.level) }}>
                        {course.level}
                      </span>
                    </div>
                  </div>
                  
                  <div className="course-description">
                    {course.description}
                  </div>
                  
                  <div className="course-progress">
                    <div className="course-progress-label">Progress: {course.progress}%</div>
                    <div className="course-progress-bar">
                      <div 
                        className="course-progress-fill"
                        style={{ 
                          width: `${course.progress}%`,
                          background: getProgressColor(course.progress)
                        }}
                      />
                    </div>
                  </div>
                  
                  <div className="course-meta">
                    <span>📅 {course.duration}</span>
                    <span>📚 {course.modules} modules</span>
                    <span>⭐ {course.xp} XP</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Achievements Section */}
          <div className="achievements-section fade-in">
            <div className="section-header">
              <h2 className="section-title">Achievements</h2>
            </div>
            
            <div className="achievements-grid">
              {achievements.map(achievement => (
                <div 
                  key={achievement.id} 
                  className={`achievement-card ${achievement.unlocked ? 'unlocked' : ''}`}
                >
                  <div className="achievement-icon">
                    {achievement.unlocked ? achievement.icon : '🔒'}
                  </div>
                  <div className="achievement-title">{achievement.title}</div>
                  <div className="achievement-description">{achievement.description}</div>
                  {achievement.unlocked && (
                    <div className="achievement-date">
                      Unlocked: {achievement.unlockedDate}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

export default iTechSmartUAIOCertification;