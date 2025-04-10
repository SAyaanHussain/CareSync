const express = require('express');
const bcrypt = require("bcrypt");
const cors = require('cors');
const session = require('express-session');
const stripe = require('stripe')('sk_test_51P4TSoSFPrVdKBVbmjp9LASNKS33nvJlYFF5lrve0DX2ld9rKePslNPDZZW21aH0MyFfeGpDv0WAuWRgMsMpeV9000LM8mZYSC');
const mongoose = require('mongoose');
const bodyParser = require('body-parser');
const app = express();
const port = 3256;
const YOUR_DOMAIN = 'http://localhost:3256';

app.use(cors());
app.use(session({
    secret: '123',
    resave: false,
    saveUninitialized: false,
    cookie: { secure: false }
}));
app.set('view engine', 'ejs');
app.use(express.static("public"));
app.use(express.json({ limit: '50mb' }));
app.use(express.urlencoded({ limit: '50mb', extended: true }));
app.use(express.json());
app.use(bodyParser.urlencoded({ extended: true }));
function connectWithRetry() {
    console.log('Connecting to MongoDB...');
    return mongoose.connect('mongodb+srv://aishahussain13579:a9831122132@adainsta.tfexlrz.mongodb.net/CareSync')
        .then(() => console.log('Connected to MongoDB'))
        .catch((err) => {
            console.error('Could not connect to MongoDB:', err.message);
            console.log('Retrying connection in 5 seconds...');
            setTimeout(connectWithRetry, 5000);
        });
}
connectWithRetry();

const userSchema = new mongoose.Schema({
    username: String,
    password: String,
    paid: { type: Boolean, default: false }
});
const User = mongoose.model('User', userSchema);

const medicationSchema = new mongoose.Schema({
    username: { type: String, required: true },
    name: { type: String, required: true },
    time: { type: String, required: true }
});
const Medication = mongoose.model('Medication', medicationSchema);

const goalSchema = new mongoose.Schema({
    username: { type: String, required: true },
    badges: [{ type: String }]
});
const Goal = mongoose.model('Goal', goalSchema);

app.get('/', (req, res) => {
    res.sendFile("templates/login.html", { root: __dirname });
});

app.get('/sign-up', (req, res) => {
    res.sendFile("templates/sign-up.html", { root: __dirname });
});

app.post('/sign', async (req, res) => {
    try {
        const { username, password } = req.body;

        const existingUser = await User.findOne({ username });
        if (existingUser) {
            return res.status(409).send("Username already exists. Please choose a different username.");
        }

        const newUser = new User({
            username: username,
            password: password
        });
        await newUser.save();
        console.log("User created successfully!");

        const session = await stripe.checkout.sessions.create({
            line_items: [
                {
                    price_data: {
                        currency: 'inr',
                        product_data: {
                            name: 'CareSync - Membership Fee (One time pay)',
                        },
                        unit_amount: 90000,
                    },
                    quantity: 1,
                },
            ],
            mode: 'payment',
            success_url: `${YOUR_DOMAIN}/success?userId=${newUser._id}`,
            cancel_url: `${YOUR_DOMAIN}/cancel`,
        });

        res.redirect(303, session.url);
    } catch (error) {
        console.error("Error creating new user:", error);
        res.status(500).send("Error creating new user, this is a server-side problem, the developers are working on it. Please try again later.");
    }
});

app.post('/login', async (req, res) => {
    try {
        const { username, password } = req.body;
        const user = await User.findOne({ username });
        if (!user) {
            return res.status(401).send("Invalid username or password");
        }
        if (password === user.password) {
            req.session.user = user;
            res.redirect("/home");
        } else {
            res.status(401).send("Invalid username or password");
        }
    } catch (error) {
        console.error("Error logging in:", error);
        res.status(500).send("Error logging in, please try again later.");
    }
});

function isAuthenticated(req, res, next) {
    console.log("Checking authentication...");
    if (req.session.user && typeof req.session.user === 'object') {
        console.log("User authenticated.");
        return next();
    } else {
        console.log("User not authenticated. Redirecting to login page.");
        res.redirect('/');
    }
}

app.get('/success', async (req, res) => {
    try {
        const userId = req.query.userId;
        await User.findByIdAndUpdate(userId, { paid: true });
        res.sendFile("templates/success.html", { root: __dirname });
    } catch (error) {
        console.error("Error updating payment status:", error);
        res.status(500).send("Error updating payment status, please try again later.");
    }
});

app.get('/cancel', (req, res) => {
    res.sendFile("templates/cancel.html", { root: __dirname });
});

app.get("/home", isAuthenticated, (req, res) => {
    console.log("Reached /home route");
    res.sendFile("templates/index.html", { root: __dirname });
});

// medication alerts
app.get("/medication-alerts", isAuthenticated, (req, res) => {
    res.sendFile("templates/reminder.html", { root: __dirname });
});

// Endpoint to add a medication
app.post('/medication-alerts/add', isAuthenticated, async (req, res) => {
    try {
        const { name, time } = req.body;
        const username = req.session.user.username;

        const newMedication = new Medication({
            username,
            name,
            time
        });

        await newMedication.save();
        res.status(201).json({ success: true, message: "Medication added successfully" });
    } catch (error) {
        console.error("Error adding medication:", error);
        res.status(500).json({ success: false, message: "Error adding medication" });
    }
});

// Endpoint to list medications
app.get('/medication-alerts/list', isAuthenticated, async (req, res) => {
    try {
        const username = req.session.user.username;
        const medications = await Medication.find({ username });

        res.json(medications);
    } catch (error) {
        console.error("Error retrieving medications:", error);
        res.status(500).json({ success: false, message: "Error retrieving medications" });
    }
});

// Endpoint to delete a medication
app.delete('/medication-alerts/delete/:id', isAuthenticated, async (req, res) => {
    try {
        const medicationId = req.params.id;
        await Medication.findByIdAndDelete(medicationId);
        res.status(200).json({ success: true, message: "Medication deleted successfully" });
    } catch (error) {
        console.error("Error deleting medication:", error);
        res.status(500).json({ success: false, message: "Error deleting medication" });
    }
});

app.get("/daily-goals", isAuthenticated, (req, res) => {
    res.sendFile("templates/games.html", { root: __dirname });
});


app.post('/daily-goals/add-badge', isAuthenticated, async (req, res) => {
    try {
        const { badge } = req.body;
        const username = req.session.user.username;

        let userGoal = await Goal.findOne({ username });
        if (!userGoal) {
            userGoal = new Goal({ username, badges: [badge] });
        } else {
            userGoal.badges.push(badge);
        }

        await userGoal.save();
        res.status(201).json({ success: true, message: "Badge added successfully" });
    } catch (error) {
        console.error("Error adding badge:", error);
        res.status(500).json({ success: false, message: "Error adding badge" });
    }
});


// Endpoint to list badges
app.get('/daily-goals/list-badges', isAuthenticated, async (req, res) => {
    try {
        const username = req.session.user.username;
        const userGoal = await Goal.findOne({ username });

        res.render('badges', { badges: userGoal ? userGoal.badges : [] });
    } catch (error) {
        console.error("Error retrieving badges:", error);
        res.status(500).render('error', { message: "Error retrieving badges" }); // Assuming you have an error.ejs template
    }
});


app.get('/boost', (req,res)=>{
    res.sendFile("templates/boost.html", { root: __dirname })
})
app.get('/boost2', (req,res)=>{
    res.sendFile("templates/boost2.html", { root: __dirname })
})
app.get('/boost3', (req,res)=>{
    res.sendFile("templates/boost3.html", { root: __dirname })
})
app.get('/boost4', (req,res)=>{
    res.sendFile("templates/boost4.html", { root: __dirname })
})
app.get('/boost5', (req,res)=>{
    res.sendFile("templates/boost5.html", { root: __dirname })
})
app.get('/boost6', (req,res)=>{
    res.sendFile("templates/boost6.html", { root: __dirname })
})
app.get('/boost7', (req,res)=>{
    res.sendFile("templates/boost7.html", { root: __dirname })
})
app.get('/msg',(req,res)=>{
    res.sendFile("templates/over.html", { root: __dirname })
})

app.get('/eyetest', (req,res)=>{
    res.sendFile("templates/eyetest.html", { root: __dirname })
})
app.get('/eyetest2', (req,res)=>{
    res.sendFile("templates/eye2.html", { root: __dirname })
})
app.get('/eyetest3', (req,res)=>{
    res.sendFile("templates/eye3.html", { root: __dirname })
})
app.get('/eyetest4', (req,res)=>{
    res.sendFile("templates/eye4.html", { root: __dirname })
})


// alt code for home page (to bypass middleware)
app.get("/*22328936A2024CareSyncuserId=22cc63hLogInSuccess", isAuthenticated, (req, res) => {
    res.redirect("/home");
});

app.listen(port, () => {
    console.log(`Server running on http://localhost:${port}`);
});



// 4000003560000008
