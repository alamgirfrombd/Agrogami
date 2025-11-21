-- PART 1: Extension, Sequences, and Table Definitions
-- Cleaned for direct execution (no pg_dump meta-commands)

-- 1) Extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- 2) Sequences
CREATE SEQUENCE IF NOT EXISTS public.auditlogs_auditid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.categories_categoryid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.customers_customerid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.inventory_inventoryid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.orderdetails_oderdetailid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.orders_orderid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.payments_paymentid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.products_productid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.roles_roleid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.userloginhistory_loginid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.userpermissions_permissionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.userprofiles_profileid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.users_userid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

CREATE SEQUENCE IF NOT EXISTS public.warehouse_warehouseid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;

-- 3) Tables

-- auditlogs
CREATE TABLE IF NOT EXISTS public.auditlogs (
    auditid bigint NOT NULL,
    userid integer,
    actiontype character varying(50) NOT NULL,
    tablename character varying(100),
    recordid character varying(100),
    actiontime timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    details text
);

ALTER TABLE public.auditlogs OWNER TO CURRENT_USER;

-- categories
CREATE TABLE IF NOT EXISTS public.categories (
    categoryid integer NOT NULL,
    categoryname character varying(100) NOT NULL
);

ALTER TABLE public.categories OWNER TO CURRENT_USER;

-- customers
CREATE TABLE IF NOT EXISTS public.customers (
    customerid integer NOT NULL,
    customercode character varying(50) NOT NULL,
    fullname character varying(200) NOT NULL,
    contactphone character varying(50),
    email character varying(200),
    region character varying(200),
    createddate timestamp without time zone NOT NULL,
    alternatephone character varying(50),
    address character varying(500),
    city character varying(100),
    postalcode character varying(20),
    customertype character varying(50),
    nid character varying(50),
    taxnumber character varying(50),
    contactperson character varying(200),
    notes text,
    isactive boolean DEFAULT true NOT NULL,
    createdby character varying(100),
    updatedby character varying(100),
    updateddate timestamp without time zone
);

ALTER TABLE public.customers OWNER TO CURRENT_USER;

-- inventory
CREATE TABLE IF NOT EXISTS public.inventory (
    inventoryid integer NOT NULL,
    productid integer NOT NULL,
    warehouseid integer NOT NULL,
    stockqty integer NOT NULL,
    lastupdate timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    purchaseprice numeric(18,4) DEFAULT 0 NOT NULL,
    salesprice numeric(18,4) DEFAULT 0 NOT NULL,
    avgcost numeric(18,4),
    reorderlevel integer DEFAULT 0,
    safetystock integer DEFAULT 0,
    maxstock integer,
    batchno character varying(50),
    expirydate date,
    unitofmeasureid integer,
    currencycode character(3) DEFAULT 'USD'::bpchar NOT NULL,
    valuationmethod character varying(20) DEFAULT 'AVG'::character varying NOT NULL,
    createdat timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    createdby character varying(100),
    updatedat timestamp without time zone,
    updatedby character varying(100),
    isactive boolean DEFAULT true NOT NULL,
    CONSTRAINT inventory_stockqty_check CHECK ((stockqty >= 0))
);

ALTER TABLE public.inventory OWNER TO CURRENT_USER;

-- orderdetails
CREATE TABLE IF NOT EXISTS public.orderdetails (
    oderdetailid integer NOT NULL,
    orderid integer NOT NULL,
    productid integer NOT NULL,
    quantity integer NOT NULL,
    unitprice numeric(18,2) NOT NULL,
    linetotal numeric(18,2) GENERATED ALWAYS AS ((quantity::numeric * unitprice)) STORED,
    CONSTRAINT orderdetails_quantity_check CHECK ((quantity > 0)),
    CONSTRAINT orderdetails_unitprice_check CHECK ((unitprice >= 0::numeric))
);

ALTER TABLE public.orderdetails OWNER TO CURRENT_USER;

-- orders
CREATE TABLE IF NOT EXISTS public.orders (
    orderid integer NOT NULL,
    ordernumber character varying(50) NOT NULL,
    customerid integer NOT NULL,
    orderdate timestamp without time zone NOT NULL,
    status character varying(50) DEFAULT 'New'::character varying NOT NULL,
    subtotal numeric(18,2) DEFAULT 0 NOT NULL,
    discount numeric(18,2) DEFAULT 0 NOT NULL,
    tax numeric(10,2) DEFAULT 0 NOT NULL,
    totalamount numeric(18,2) DEFAULT 0 NOT NULL,
    CONSTRAINT orders_discount_check CHECK ((discount >= 0::numeric)),
    CONSTRAINT orders_subtotal_check CHECK ((subtotal >= 0::numeric)),
    CONSTRAINT orders_tax_check CHECK ((tax >= 0::numeric)),
    CONSTRAINT orders_totalamount_check CHECK ((totalamount >= 0::numeric))
);

ALTER TABLE public.orders OWNER TO CURRENT_USER;

-- payments
CREATE TABLE IF NOT EXISTS public.payments (
    paymentid integer NOT NULL,
    orderid integer NOT NULL,
    paymentdate timestamp without time zone NOT NULL,
    amount numeric(18,2) NOT NULL,
    paymentmethod character varying(50) NOT NULL,
    transactionref character varying(200),
    CONSTRAINT payments_amount_check CHECK ((amount >= 0::numeric))
);

ALTER TABLE public.payments OWNER TO CURRENT_USER;

-- products
CREATE TABLE IF NOT EXISTS public.products (
    productid integer NOT NULL,
    sku character varying(50) NOT NULL,
    productname character varying(200) NOT NULL,
    categoryid integer NOT NULL,
    unitprice numeric(18,2) DEFAULT 0 NOT NULL,
    isactive boolean DEFAULT true NOT NULL
);

ALTER TABLE public.products OWNER TO CURRENT_USER;

-- roles
CREATE TABLE IF NOT EXISTS public.roles (
    roleid integer NOT NULL,
    rolename character varying(50) NOT NULL,
    description character varying(255),
    issystemrole boolean DEFAULT false NOT NULL,
    createdat timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updatedat timestamp without time zone
);

ALTER TABLE public.roles OWNER TO CURRENT_USER;

-- userloginhistory
CREATE TABLE IF NOT EXISTS public.userloginhistory (
    loginid bigint NOT NULL,
    userid integer NOT NULL,
    logintime timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    logouttime timestamp without time zone,
    ipaddress character varying(45),
    deviceinfo character varying(255),
    status character varying(20) DEFAULT 'Success'::character varying NOT NULL
);

ALTER TABLE public.userloginhistory OWNER TO CURRENT_USER;

-- userpermissions
CREATE TABLE IF NOT EXISTS public.userpermissions (
    permissionid integer NOT NULL,
    userid integer NOT NULL,
    modulename character varying(100) NOT NULL,
    permissionvalue integer NOT NULL,
    createdat timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);

ALTER TABLE public.userpermissions OWNER TO CURRENT_USER;

-- userprofiles
CREATE TABLE IF NOT EXISTS public.userprofiles (
    profileid integer NOT NULL,
    userid integer NOT NULL,
    address character varying(255),
    city character varying(100),
    country character varying(100),
    dateofbirth date,
    gender character varying(10),
    profilepictureurl character varying(255),
    createdat timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updatedat timestamp without time zone
);

ALTER TABLE public.userprofiles OWNER TO CURRENT_USER;

-- users
CREATE TABLE IF NOT EXISTS public.users (
    userid integer NOT NULL,
    username character varying(100) NOT NULL,
    fullname character varying(150) NOT NULL,
    email character varying(150) NOT NULL,
    phonenumber character varying(20),
    passwordhash character varying(255) NOT NULL,
    roleid integer NOT NULL,
    isactive boolean DEFAULT true NOT NULL,
    lastlogin timestamp without time zone,
    createdat timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updatedat timestamp without time zone
);

ALTER TABLE public.users OWNER TO CURRENT_USER;

-- warehouse
CREATE TABLE IF NOT EXISTS public.warehouse (
    warehouseid integer NOT NULL,
    warehousename character varying(200) NOT NULL,
    location character varying(200)
);

ALTER TABLE public.warehouse OWNER TO CURRENT_USER;

-- 4) Attach sequences as owned by columns (so DROP/OWN works properly)
ALTER SEQUENCE IF EXISTS public.auditlogs_auditid_seq OWNED BY public.auditlogs.auditid;
ALTER SEQUENCE IF EXISTS public.categories_categoryid_seq OWNED BY public.categories.categoryid;
ALTER SEQUENCE IF EXISTS public.customers_customerid_seq OWNED BY public.customers.customerid;
ALTER SEQUENCE IF EXISTS public.inventory_inventoryid_seq OWNED BY public.inventory.inventoryid;
ALTER SEQUENCE IF EXISTS public.orderdetails_oderdetailid_seq OWNED BY public.orderdetails.oderdetailid;
ALTER SEQUENCE IF EXISTS public.orders_orderid_seq OWNED BY public.orders.orderid;
ALTER SEQUENCE IF EXISTS public.payments_paymentid_seq OWNED BY public.payments.paymentid;
ALTER SEQUENCE IF EXISTS public.products_productid_seq OWNED BY public.products.productid;
ALTER SEQUENCE IF EXISTS public.roles_roleid_seq OWNED BY public.roles.roleid;
ALTER SEQUENCE IF EXISTS public.userloginhistory_loginid_seq OWNED BY public.userloginhistory.loginid;
ALTER SEQUENCE IF EXISTS public.userpermissions_permissionid_seq OWNED BY public.userpermissions.permissionid;
ALTER SEQUENCE IF EXISTS public.userprofiles_profileid_seq OWNED BY public.userprofiles.profileid;
ALTER SEQUENCE IF EXISTS public.users_userid_seq OWNED BY public.users.userid;
ALTER SEQUENCE IF EXISTS public.warehouse_warehouseid_seq OWNED BY public.warehouse.warehouseid;

-- 5) Set default values to use sequences (only if column has no default yet)
ALTER TABLE ONLY public.auditlogs ALTER COLUMN auditid SET DEFAULT nextval('public.auditlogs_auditid_seq'::regclass);
ALTER TABLE ONLY public.categories ALTER COLUMN categoryid SET DEFAULT nextval('public.categories_categoryid_seq'::regclass);
ALTER TABLE ONLY public.customers ALTER COLUMN customerid SET DEFAULT nextval('public.customers_customerid_seq'::regclass);
ALTER TABLE ONLY public.inventory ALTER COLUMN inventoryid SET DEFAULT nextval('public.inventory_inventoryid_seq'::regclass);
ALTER TABLE ONLY public.orderdetails ALTER COLUMN oderdetailid SET DEFAULT nextval('public.orderdetails_oderdetailid_seq'::regclass);
ALTER TABLE ONLY public.orders ALTER COLUMN orderid SET DEFAULT nextval('public.orders_orderid_seq'::regclass);
ALTER TABLE ONLY public.payments ALTER COLUMN paymentid SET DEFAULT nextval('public.payments_paymentid_seq'::regclass);
ALTER TABLE ONLY public.products ALTER COLUMN productid SET DEFAULT nextval('public.products_productid_seq'::regclass);
ALTER TABLE ONLY public.roles ALTER COLUMN roleid SET DEFAULT nextval('public.roles_roleid_seq'::regclass);
ALTER TABLE ONLY public.userloginhistory ALTER COLUMN loginid SET DEFAULT nextval('public.userloginhistory_loginid_seq'::regclass);
ALTER TABLE ONLY public.userpermissions ALTER COLUMN permissionid SET DEFAULT nextval('public.userpermissions_permissionid_seq'::regclass);
ALTER TABLE ONLY public.userprofiles ALTER COLUMN profileid SET DEFAULT nextval('public.userprofiles_profileid_seq'::regclass);
ALTER TABLE ONLY public.users ALTER COLUMN userid SET DEFAULT nextval('public.users_userid_seq'::regclass);
ALTER TABLE ONLY public.warehouse ALTER COLUMN warehouseid SET DEFAULT nextval('public.warehouse_warehouseid_seq'::regclass);

-- End of Part 1
-- PART 2: COPY DATA INTO TABLES
-- Cleaned COPY statements (fully compatible)

-- categories
COPY public.categories (categoryid, categoryname) FROM stdin;
65	Computer
66	Laptop
68	Mobile
71	Samsung
\.

-- customers
COPY public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) FROM stdin;
100003	CUST-000001	Alamgir Kabir	01712706040	alamgirkabir.wave@gmail.com	Dhaka	2025-11-19 15:29:05.839915	01841338354	Flat # A5, Block-R, House # 48, Block : R/S, Nurjahan Road, Mohammadpur, Dhaka	Dhaka	1207	Retail	123456789101		Test for Delete	He is the Regula customer	t	Admin	Admin	2025-11-19 16:10:21.005352
100005	CUST-000002	Hasan Mahmud	01711000002	hasan@example.com	Dhaka	2025-11-19 16:14:17.216667	01841000002	Mirpur DOHS, Dhaka	Dhaka	1216	Retail	987654321012	\N	Mr. Jui	New customer	t	Admin	\N	\N
100006	CUST-000003	Shamim Ahmed	01711000003	shamim@example.com	Chattogram	2025-11-19 16:14:17.216667	01841000003	Noman Society, Agrabad	Chattogram	4000	Dealer	998877665544	\N	Mr. Imtiaz	Good relationship	t	Admin	\N	\N
100007	CUST-000004	Runa Akter	01711000004	runa@example.com	Sylhet	2025-11-19 16:14:17.216667	01841000004	Zindabazar, Sylhet	Sylhet	3100	Retail	112233445566	\N	Ms. Lima	Frequent buyer	t	Admin	\N	\N
100008	CUST-000005	Fahim Khan	01711000005	fahim@example.com	Khulna	2025-11-19 16:14:17.216667	01841000005	Sonadanga, Khulna	Khulna	9000	Dealer	556677889900	123456789	Mr. Rashed	Corporate client	t	Admin	Admin	2025-11-20 05:11:40.698994
100009	CUST-000006	Jannat Ara	01711000006	jannat@example.com	Rajshahi	2025-11-19 16:14:17.216667	01841000006	Shaheb Bazar, Rajshahi	Rajshahi	6000	Retail	778899001122	\N	Ms. Asha	Occasional buyer	t	Admin	\N	\N
100010	CUST-000007	Rahim Uddin	01711000007	rahim@example.com	Barishal	2025-11-19 16:14:17.216667	01841000007	Band Road, Barishal	Barishal	8200	Dealer	445566778899	\N	Mr. Rubel	Local dealer	t	Admin	\N	\N
100011	CUST-000008	Farzana Rahman	01711000008	farzana@example.com	Rangpur	2025-11-19 16:14:17.216667	01841000008	Rangpur Sadar, Rangpur	Rangpur	5400	VIP	667788990011	\N	Ms. Priya	High-value customer	t	Admin	\N	\N
100013	CUST-000010	Sumaiya Islam	01711000010	sumaiya@example.com	Narayanganj	2025-11-19 16:14:17.216667	01841000010	Fatullah, Narayanganj	Narayanganj	1400	Retail	223344556677	\N	Ms. Shila	New customer	t	Admin	\N	\N
100014	CUST-000011	Rezaul Karim	01711000011	rezaul@example.com	Mymensingh	2025-11-19 16:14:17.216667	01841000011	Town Hall, Mymensingh	Mymensingh	2200	Retail	990011223344		Mr. Adnan	Monthly buyer	t	Admin	Admin	2025-11-20 05:11:19.75076
100016	CUST-100015	Alamgir Kabir	01712706041			2025-11-20 07:48:35.469217			খুলনা		Retail	12345678	123456	Fahim Khan	এনআইডি ও ট্যাক্স ভ্যালিডেশন দিতে হবে	t	Admin	\N	2025-11-20 07:50:49.675525
\.

-- inventory
COPY public.inventory (inventoryid, productid, warehouseid, stockqty, lastupdate, purchaseprice, salesprice, avgcost, reorderlevel, safetystock, maxstock, batchno, expirydate, unitofmeasureid, currencycode, valuationmethod, createdat, createdby, updatedat, updatedby, isactive) FROM stdin;
50013	8	1	2	2025-11-19 11:21:57.186094	50000.0000	0.0000	\N	0	0	\N	\N	\N	\N	USD	AVG	2025-11-19 11:01:53.286535	\N	\N	\N	t
50015	7	1	2	2025-11-20 19:42:19.520481	0.0000	0.0000	\N	0	0	\N	\N	\N	\N	USD	AVG	2025-11-21 01:37:21.383933	\N	\N	\N	t
50014	11	2	2	2025-11-20 19:42:23.484822	50000.0000	0.0000	\N	0	0	\N	\N	\N	\N	USD	AVG	2025-11-19 11:22:42.560897	\N	\N	\N	t
\.

-- products
COPY public.products (productid, sku, productname, categoryid, unitprice, isactive) FROM stdin;
10	LAP-6601	Samsung Smart TV 43 Inch	66	55000.00	t
11	SAM-7101	6.5 Inch Android 20 Phone	71	15000.00	t
12	LAP-6602	Dell Laptop	66	51000.00	t
13	COM-6502	Core I Seven, Dell	65	99000.00	t
14	MOB-6801	Techno 14	68	19999.00	t
15	LAP-6603	Desktop Coputer	66	99999.00	t
16	COM-6503	Desktop Computer	65	99999.00	t
8	COM-6504	HP Laptop 14th Generation	65	28000.00	t
7	LAP-6604	Dell Inspiron Laptop 13th Gen	66	72000.00	f
\.

-- orders
COPY public.orders (orderid, ordernumber, customerid, orderdate, status, subtotal, discount, tax, totalamount) FROM stdin;
200032	20251120-0001	100005	2025-11-19 00:00:00	Pending	15000.00	0.00	0.00	15000.00
200031	001	100016	2025-11-20 00:00:00	Pending	10000.00	10.00	1.00	9991.00
\.

-- orderdetails
COPY public.orderdetails (oderdetailid, orderid, productid, quantity, unitprice) FROM stdin;
1	200031	8	1	28000.00
2	200031	11	3	17000.00
4	200032	7	1	72000.00
5	200032	11	1	15000.00
6	200032	14	2	19999.00
7	200031	13	3	99000.00
\.

-- payments
COPY public.payments (paymentid, orderid, paymentdate, amount, paymentmethod, transactionref) FROM stdin;
2	200032	2025-11-21 00:00:00	3000.00	Card	2
\.

-- PART 3: Remaining COPY DATA (roles, users, permissions, warehouse etc.)

-- roles
COPY public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) FROM stdin;
1	Administrator	Full access	t	2025-11-13 17:25:57.673333	2025-11-13 20:45:34.986667
2	Manager	Can oversee operations and manage user activities.	f	2025-11-13 17:25:57.673333	\N
3	Data Analyst	Can view and analyze data reports and dashboards.	t	2025-11-13 17:25:57.673333	2025-11-13 20:45:58.943333
4	Accountant	Responsible for managing financial transactions and reports.	f	2025-11-13 17:25:57.673333	\N
6	Loan Officer	Create Loan	f	2025-11-13 20:00:45.313333	2025-11-13 20:00:45.313333
7	Area Manager	safws asfds	f	2025-11-13 20:14:51.126667	2025-11-13 20:14:51.126667
8	Regional Manager	Regional manger can only ready Data	f	2025-11-13 20:27:39.276667	2025-11-13 20:27:39.276667
9	CDO	sdfsd fdsfs	f	2025-11-20 17:34:56.88174	2025-11-20 17:39:04.419635
\.

-- users
COPY public.users (userid, username, fullname, email, phonenumber, passwordhash, roleid, isactive, lastlogin, createdat, updatedat) FROM stdin;
1	Alamgir	Alamgir Kabir	alamgirfrombd@gmail.com	01712706040	hashed_password_here	7	t	\N	2025-11-15 19:51:59.07	2025-11-15 21:41:18.606979
4	Beauty	Hafiza Khatun	hafiza@gmail.com	01931670959	$2b$12$tUfZ77p2tI7uARoatpCylenZq4xo3hOCL/3aXMeS77E7MNsNjIhtS	7	t	\N	2025-11-15 21:35:59.050281	2025-11-15 21:35:59.050281
5	Rifat	Rifat Muzakkir	rifat@gmail.com	01841338354	$2b$12$O1vBDVBjaXX9Qo3aaI30MeTNYvyvi54eT62wzq7s1HRZm0z5jXnu6	3	t	\N	2025-11-15 21:42:10.669953	2025-11-16 09:10:16.972464
3	abony	Promity Abony	abon@gmail.com	01711706040	Alamgir@123	1	t	\N	2025-11-15 20:45:39.718651	2025-11-20 17:51:21.842912
\.

-- userloginhistory
COPY public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) FROM stdin;
1	1	2025-11-18 10:30:07.186667	2025-11-18 10:32:16.363333	192.168.0.207	Windows 10	Success
2	1	2025-11-18 10:32:20.686667	\N	192.168.0.207	Windows 10	Success
3	1	2025-11-18 10:36:34.476667	\N	192.168.0.207	Windows 10	Success
4	1	2025-11-18 10:39:48.623333	\N	192.168.0.207	Windows 10	Success
5	1	2025-11-18 10:40:03.23	\N	192.168.0.207	Windows 10	Success
6	1	2025-11-18 10:41:57.073333	\N	192.168.0.207	Windows 10	Success
7	1	2025-11-18 10:43:16.083333	\N	192.168.0.207	Windows 10	Success
8	1	2025-11-18 10:43:17.18	\N	192.168.0.207	Windows 10	Success
9	1	2025-11-18 10:43:17.88	\N	192.168.0.207	Windows 10	Success
10	1	2025-11-18 10:43:18.88	\N	192.168.0.207	Windows 10	Success
11	1	2025-11-18 10:43:50.636667	\N	192.168.0.207	Windows 10	Success
12	1	2025-11-18 10:43:51.196667	\N	192.168.0.207	Windows 10	Success
13	1	2025-11-18 10:48:31.133333	\N	192.168.0.207	Windows 10	Success
14	1	2025-11-18 10:50:15.706667	\N	192.168.0.207	Windows 10	Success
15	1	2025-11-18 10:52:21.896667	\N	192.168.0.207	Windows 10	Success
\.

-- userpermissions
COPY public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) FROM stdin;
1	1	Users	15	2025-11-16 17:06:17.240023
2	1	Auth	15	2025-11-16 17:11:32.67006
3	3	Auth	15	2025-11-16 17:17:57.400763
4	3	Users	7	2025-11-16 17:30:24.502772
5	3	Roles	15	2025-11-16 17:17:57.416752
6	3	Permissions	15	2025-11-16 17:17:57.420373
7	3	UserProfiles	15	2025-11-16 17:17:57.426356
8	3	UserLoginHistory	15	2025-11-16 17:17:57.433529
9	3	AuditLogs	15	2025-11-16 17:17:57.438009
10	3	AdminDashboard	15	2025-11-16 17:17:57.442202
11	3	ShopDashboard	15	2025-11-16 17:17:57.448134
12	3	UserDashboard	15	2025-11-16 17:17:57.454316
13	3	ShopManagement	15	2025-11-16 17:17:57.457439
14	3	SalesManagement	15	2025-11-16 17:17:57.460482
15	3	InventoryManagement	15	2025-11-16 17:17:57.468075
16	3	CustomerManagement	15	2025-11-16 17:17:57.47711
17	3	LoanManagement	15	2025-11-16 17:17:57.483383
18	3	PaymentManagement	15	2025-11-16 17:17:57.48508
\.

-- userprofiles
COPY public.userprofiles (profileid, userid, address, city, country, dateofbirth, gender, profilepictureurl, createdat, updatedat) FROM stdin;
5	1	House #12, Road #5, Dhanmondi	Dhaka	Bangladesh	1990-05-12	Male	https://example.com/profiles/alamgir.jpg	2025-11-16 09:44:53.756667	\N
8	1	Flat # A5, Block-R, House # 48, Block : R/S, Nurjahan Road, Mohammadpur, Dhaka	Dhaka	Bangladesh	1979-11-06	Male	uploads/profile_pics\\user_1.JPG	2025-11-16 13:03:44.30145	2025-11-20 20:45:54.412014
\.

-- warehouse
COPY public.warehouse (warehouseid, warehousename, location) FROM stdin;
1	Central Warehouse	Dhaka
2	North Hub	Chittagong
3	South Hub	Khulna
4	East Depot	Sylhet
5	West Depot	Rajshahi
6	City Storage 1	Dhaka
7	City Storage 2	Chittagong
10	City Storage 5	Rajshahi
11	Main Distribution Center	Dhaka
12	Backup Warehouse	Chittagong
13	Temporary Storage 1	Khulna
14	Temporary Storage 2	Sylhet
15	Temporary Storage 3	Rajshahi
16	North-East Storage	Sylhet
17	North-West Storage	Rajshahi
18	South-East Storage	Chittagong
19	South-West Storage	Khulna
20	Industrial Warehouse 1	Dhaka
21	Industrial Warehouse 2	Chittagong
22	Industrial Warehouse 3	Khulna
23	Industrial Warehouse 4	Sylhet
24	Industrial Warehouse 5	Rajshahi
25	Standard Depot 1	Dhaka
26	Standard Depot 2	Chittagong
27	Standard Depot 3	Khulna
28	Standard Depot 4	Sylhet
29	Standard Depot 5	Rajshahi
30	Logistics Hub 1	Dhaka
31	Logistics Hub 2	Chittagong
32	Logistics Hub 3	Khulna
33	Logistics Hub 4	Sylhet
34	Logistics Hub 5	Rajshahi
35	Warehouse Alpha	Dhaka
36	Warehouse Beta	Chittagong
37	Warehouse Gamma	Khulna
38	Warehouse Delta	Sylhet
39	Warehouse Epsilon	Rajshahi
40	Regional Hub 1	Dhaka
41	Regional Hub 2	Chittagong
42	Regional Hub 3	Khulনা
43	Regional Hub 4	Sylhet
44	Regional Hub 5	Rajshahi
45	City Hub A	Dhaka
46	City Hub B	Chittagong
47	City Hub C	Khulna
49	Jhenaidah_Alamgir	Rajshahi
50	Power House	Chuadanga
9	City Storage 50	Sylhet
\.


-- PART 4: CONSTRAINTS AND FOREIGN KEYS
-- (Final section of the migration)

-- PRIMARY KEYS
ALTER TABLE ONLY public.auditlogs
    ADD CONSTRAINT auditlogs_pkey PRIMARY KEY (auditid);

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (categoryid);

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customerid);

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (inventoryid);

ALTER TABLE ONLY public.orderdetails
    ADD CONSTRAINT orderdetails_pkey PRIMARY KEY (oderdetailid);

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (orderid);

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (paymentid);

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (productid);

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (roleid);

ALTER TABLE ONLY public.userloginhistory
    ADD CONSTRAINT userloginhistory_pkey PRIMARY KEY (loginid);

ALTER TABLE ONLY public.userpermissions
    ADD CONSTRAINT userpermissions_pkey PRIMARY KEY (permissionid);

ALTER TABLE ONLY public.userprofiles
    ADD CONSTRAINT userprofiles_pkey PRIMARY KEY (profileid);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);

ALTER TABLE ONLY public.warehouse
    ADD CONSTRAINT warehouse_pkey PRIMARY KEY (warehouseid);

-- UNIQUE CONSTRAINTS
ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_customercode_key UNIQUE (customercode);

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_sku_key UNIQUE (sku);

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_ordernumber_key UNIQUE (ordernumber);

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_rolename_key UNIQUE (rolename);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_productid_warehouseid_key UNIQUE (productid, warehouseid);

-- FOREIGN KEYS
ALTER TABLE ONLY public.auditlogs
    ADD CONSTRAINT fk_auditlogs_userid
    FOREIGN KEY (userid) REFERENCES public.users(userid);

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT fk_inventory_productsid
    FOREIGN KEY (productid) REFERENCES public.products(productid);

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT fk_inventory_warehouseid
    FOREIGN KEY (warehouseid) REFERENCES public.warehouse(warehouseid);

ALTER TABLE ONLY public.orderdetails
    ADD CONSTRAINT fk_orderdetails_orderid
    FOREIGN KEY (orderid) REFERENCES public.orders(orderid) ON DELETE CASCADE;

ALTER TABLE ONLY public.orderdetails
    ADD CONSTRAINT fk_orderdetails_productid
    FOREIGN KEY (productid) REFERENCES public.products(productid);

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_customerid
    FOREIGN KEY (customerid) REFERENCES public.customers(customerid);

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_payments_orders
    FOREIGN KEY (orderid) REFERENCES public.orders(orderid);

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_category
    FOREIGN KEY (categoryid) REFERENCES public.categories(categoryid);

ALTER TABLE ONLY public.userloginhistory
    ADD CONSTRAINT fk_userloginhistory_userid
    FOREIGN KEY (userid) REFERENCES public.users(userid);

ALTER TABLE ONLY public.userpermissions
    ADD CONSTRAINT fk_userpermissions_userid
    FOREIGN KEY (userid) REFERENCES public.users(userid);

ALTER TABLE ONLY public.userprofiles
    ADD CONSTRAINT fk_userprofiles_userid
    FOREIGN KEY (userid) REFERENCES public.users(userid);

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_roleid
    FOREIGN KEY (roleid) REFERENCES public.roles(roleid);
