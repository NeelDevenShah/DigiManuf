const jwt = require('jsonwebtoken')
const JWT_SECRET = process.env.SECRET_KEY;
const User = require("../models/user")

const verifyuser = async(req, res, next) => {
    
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
        const userOrg = user.organization; // Assuming the token contains organization info
        
        if (!userOrg) {
            return res.status(403).json({ error: 'Access Denied: No organization found for user' });
        }
        // Attach organization ID to request for use in the controller
        req.userOrg = userOrg;
        req.user = user;

        next();  // Proceed to the controller logic
    } catch (error) {
        console.log(error);
        return res.status(403).json({ error: 'Access denied: Invalid token' });
    }
}

module.exports = verifyuser

