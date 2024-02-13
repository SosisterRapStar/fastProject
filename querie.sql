SELECT * FROM conversation
JOIN user_conversation uc
    ON conversation.id = uc.conversation_id
JOIN "user" u
    ON u.id = uc.user_id
WHERE u.name = 'I hate niggers'
