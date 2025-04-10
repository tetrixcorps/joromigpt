   -- queries/training_data.sql
   SELECT 
       id,
       question,
       answer,
       category,
       difficulty,
       created_at
   FROM 
       training_samples
   WHERE 
       is_validated = true
       AND created_at > NOW() - INTERVAL '30 days'
   ORDER BY 
       created_at DESC
   LIMIT 10000;
