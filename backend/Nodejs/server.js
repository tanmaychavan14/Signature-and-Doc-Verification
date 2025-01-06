const express = require('express');
const axios = require('axios');
const fs = require('fs');
const FormData = require('form-data');
const path = require('path');

// Setup Express server
const app = express();
const port = 4000;

// Endpoint to trigger signature verification
app.post('/verify-signature', async (req, res) => {
    // Define paths to the pre-existing files in the 'uploads/' folder
    const originalSignaturePath = path.join(__dirname, 'uploads', 'original_signature.jpg');
    const verificationSignaturePath = path.join(__dirname, 'uploads', 'verification_signature.jpg');

    // Check if both files exist
    if (!fs.existsSync(originalSignaturePath) || !fs.existsSync(verificationSignaturePath)) {
        return res.status(400).send('Both original and verification signature files must exist in the uploads folder');
    }

    try {
        // Create FormData object
        const form = new FormData();
        form.append('original_signature', fs.createReadStream(originalSignaturePath));
        form.append('verification_signature', fs.createReadStream(verificationSignaturePath));

        // Send the form data to FastAPI
        const response = await axios.post('http://127.0.0.1:8000/verify-signature/', form, {
            headers: form.getHeaders(),
        });

        // Return the result from FastAPI to the client
        res.json(response.data);
    } catch (error) {
        console.error('Error verifying signature:', error.response ? error.response.data : error.message);
        res.status(500).send('Internal Server Error');
    }
});

// Start Node.js server
app.listen(port, () => {
    console.log(`Node.js server running at http://localhost:${port}`);
});
