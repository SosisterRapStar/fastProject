SELECT "user".name, "user".email, "user".password, "user".created_at, "user".id
FROM "user"
WHERE "user".name = 'I hate niggers';
SELECT user_1.id AS user_1_id, conversation.name AS conversation_name, conversation.user_admin_fk AS conversation_user_admin_fk, conversation.created_at AS conversation_created_at, conversation.updated_at AS conversation_updated_at, conversation.id AS conversation_id
FROM "user" AS user_1 JOIN user_conversation AS user_conversation_1 ON user_1.id = user_conversation_1.user_fk JOIN conversation ON conversation.id = user_conversation_1.conversation_fk
WHERE user_1.id IN ('3d0503bb-2cb3-440c-ae2d-e2818e862595'::UUID)