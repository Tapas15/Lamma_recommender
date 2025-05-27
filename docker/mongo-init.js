// MongoDB initialization script for Job Recommender Application

// Switch to the job_recommender database
db = db.getSiblingDB('job_recommender');

// Create collections with validation schemas
db.createCollection('users', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['email', 'password_hash', 'user_type', 'full_name'],
      properties: {
        email: {
          bsonType: 'string',
          pattern: '^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        },
        user_type: {
          bsonType: 'string',
          enum: ['candidate', 'employer']
        },
        full_name: {
          bsonType: 'string',
          minLength: 1
        }
      }
    }
  }
});

db.createCollection('jobs', {
  validator: {
    $jsonSchema: {
      bsonType: 'object',
      required: ['title', 'company', 'employer_id'],
      properties: {
        title: {
          bsonType: 'string',
          minLength: 1
        },
        company: {
          bsonType: 'string',
          minLength: 1
        },
        status: {
          bsonType: 'string',
          enum: ['active', 'inactive', 'closed']
        }
      }
    }
  }
});

db.createCollection('applications');
db.createCollection('recommendations');
db.createCollection('feedback');
db.createCollection('skill_clusters');
db.createCollection('market_trends');

// Create indexes for better performance
db.users.createIndex({ email: 1 }, { unique: true });
db.users.createIndex({ user_type: 1 });
db.users.createIndex({ 'skills.languages_frameworks': 1 });

db.jobs.createIndex({ employer_id: 1 });
db.jobs.createIndex({ status: 1 });
db.jobs.createIndex({ 'required_skills': 1 });
db.jobs.createIndex({ location: 1 });
db.jobs.createIndex({ created_at: -1 });

db.applications.createIndex({ candidate_id: 1 });
db.applications.createIndex({ job_id: 1 });
db.applications.createIndex({ status: 1 });

db.recommendations.createIndex({ user_id: 1 });
db.recommendations.createIndex({ recommendation_type: 1 });
db.recommendations.createIndex({ created_at: -1 });

db.feedback.createIndex({ user_id: 1 });
db.feedback.createIndex({ recommendation_id: 1 });
db.feedback.createIndex({ created_at: -1 });

// Insert sample data (optional)
print('MongoDB initialization completed for Job Recommender Application');
print('Collections created: users, jobs, applications, recommendations, feedback, skill_clusters, market_trends');
print('Indexes created for optimal performance'); 