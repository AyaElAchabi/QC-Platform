-- Supprimer les utilisateurs de test s'ils existent déjà
DELETE FROM users WHERE email IN ('admin@test.com', 'chef@test.com', 'operator@test.com', 'viewer@test.com');

-- Créer les utilisateurs de test (mot de passe: password123)
INSERT INTO users (email, password_hash, role, is_active, email_verified, full_name) VALUES
('admin@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeK9NnqVqGSW', 'ADMIN', true, true, 'Admin Test'),
('chef@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeK9NnqVqGSW', 'CHEF_OPERATOR', true, true, 'Chef Test'),
('operator@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeK9NnqVqGSW', 'OPERATOR', true, true, 'Operator Test'),
('viewer@test.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5oeK9NnqVqGSW', 'VIEWER', true, true, 'Viewer Test');

-- Afficher les utilisateurs créés
SELECT email, role, is_active, full_name FROM users WHERE email LIKE '%test.com' ORDER BY role;
