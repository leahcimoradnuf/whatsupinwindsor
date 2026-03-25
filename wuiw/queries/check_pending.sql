SELECT meeting_id, meeting_type, materials, status
FROM assignments
LEFT JOIN articles ON assignments.meeting_id = articles.meeting_id
WHERE assignments.status = 'pending' AND articles.meeting_id IS NULL;