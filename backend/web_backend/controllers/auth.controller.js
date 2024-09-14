var User = require('../models/user.js');
var jwt = require('jsonwebtoken');
const bcrypt = require('bcryptjs')
const dotenv = require('dotenv');
dotenv.config();
const generateToken = require('../middleware/token.js')
const SECRET_KEY = process.env.SECRET_KEY;

exports.register = async (req, res) => {
    try{
        console.log('REQ BODY ON REGISTER CONTROLLER', req.body);
        let user = await req.body;
        console.log(user)
        if (await User.findOne({ email : user.email })) {
            return res.status(400).json({ error: 'User already exists'  });
        }

        let salt = await bcrypt.genSalt(10); 
        let secpass =  await bcrypt.hash(user.password, salt);

        user.password = secpass;
        let create = await User.create(user);

        if (create) {
            return res.status(201).json({ message: 'User created successfully' });  
        } else {
            return res.status(400).json({ error: 'User not created' });
        }
    }

    catch (error) {
        console.log(error);
        return res.status(500).json({ error: 'Internal server error' });
} 
}

exports.login = async (req, res) => {
    try {

        let user = await User.findOne({ email: req.body.email })
        if (!user) {
            console.log("no user")
            return res.status(401).json({ error: "Invalid Credentials" })
        }

        if (user.isblocked) {
            return res.status(401).json({ error: "You are blocked" })
        }

        let vaildpass = await bcrypt.compare(req.body.password, user.password)

        if (!vaildpass) {
            console.log("invalid pass")
            return res.status(401).json({ error: "Invalid Credentials" })
        }
       
        // Generating token for authenticated user
        generateToken(res, user.id)
        console.log("logged in")
        return res.status(200).json({ success: "logged in" })

    } 
    catch (error) {
        console.log(error)

        return res.status(500).json({ error: "Internal error" })
    }
}
// module.exports = forgotPassword = (req, res) => {}

    exports.resetPassword = async (req, res) => {
        try {
            const token = req.cookies.token;
            if (!token) {
                return res.status(401).json({ error: 'Unauthorized' });
            }
    
            const decoded = jwt.verify(token, SECRET_KEY);
            const id = decoded.userId;
            if (!id) {
                return res.status(401).json({ error: 'Unauthorized' });
            }
    
            const user = await User.findById(id); // Ensure to await the async operation
            if (!user) {
                return res.status(404).json({ error: 'User not found' });
            }
    
            const salt = await bcrypt.genSalt(10); // Ensure to await the async operation
            const newpass = await bcrypt.hash(req.body.password, salt); // Ensure to await the async operation
    
            user.password = newpass;
            await user.save(); // Ensure to await the async operation
    
            return res.status(200).json({ message: 'Password reset successfully' }); // Send success response
        } catch (error) {
            console.log(error);
            return res.status(500).json({ error: 'Internal server error' });
        }
    }

// module.exports = changePassword = (req, res) => {}




