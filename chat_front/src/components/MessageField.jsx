import React, {useState} from 'react'
import styles from './messagefield.module.scss'


const MessageField = () => {
    const [message, setMessage] = useState("")

    // const handleEnter = (event) => {
    //     if (event.key === 'Enter') {
    //         handleSend();
    //     }
    // };

    const [text, setText] = useState('');

    const handleInput = (event) => {
        const textarea = event.target;
        textarea.style.height = 'auto'; // Reset height
        textarea.style.height = `${textarea.scrollHeight}px`; // Set height to scrollHeight
        setText(textarea.value); // Update the state with the input text
    };


    return(
        <div className={styles.messageFieldContainer}>
            <textarea
            value={text}
            onChange={handleInput}
            placeholder="Type your message..."
            rows="1"
            className="auto-resize-textarea w-full p-2 border rounded resize-none overflow-hidden"
            style={{ height: 'auto', lineHeight: '1.5', fontSize: '16px' }}
        />
            <button className={styles.sendButton}>
                <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="size-6">
                <path strokeLinecap="round" strokeLinejoin="round" d="M6 12 3.269 3.125A59.769 59.769 0 0 1 21.485 12 59.768 59.768 0 0 1 3.27 20.875L5.999 12Zm0 0h7.5" />
                </svg>
            </button>
        </div>
    )

}

export default MessageField