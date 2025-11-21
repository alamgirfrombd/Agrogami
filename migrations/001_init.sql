--
-- PostgreSQL database dump
--


-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.0

-- Started on 2025-11-21 15:51:18

SELECT pg_catalog.set_config('search_path', '', false);

--
-- TOC entry 2 (class 3079 OID 16606)
-- Name: uuid-ossp; Type: EXTENSION; Schema: -; Owner: -
--



--
-- TOC entry 5215 (class 0 OID 0)
-- Dependencies: 2
-- Name: EXTENSION "uuid-ossp"; Type: COMMENT; Schema: -; Owner: 
--





--
-- TOC entry 221 (class 1259 OID 16618)
-- Name: auditlogs; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.auditlogs (
    auditid bigint NOT NULL,
    userid integer,
    actiontype character varying(50) NOT NULL,
    tablename character varying(100),
    recordid character varying(100),
    actiontime timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    details text
);



--
-- TOC entry 220 (class 1259 OID 16617)
-- Name: auditlogs_auditid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.auditlogs_auditid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5216 (class 0 OID 0)
-- Dependencies: 220
-- Name: auditlogs_auditid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.auditlogs_auditid_seq OWNED BY public.auditlogs.auditid;


--
-- TOC entry 223 (class 1259 OID 16631)
-- Name: categories; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.categories (
    categoryid integer NOT NULL,
    categoryname character varying(100) NOT NULL
);



--
-- TOC entry 222 (class 1259 OID 16630)
-- Name: categories_categoryid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.categories_categoryid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5217 (class 0 OID 0)
-- Dependencies: 222
-- Name: categories_categoryid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.categories_categoryid_seq OWNED BY public.categories.categoryid;


--
-- TOC entry 225 (class 1259 OID 16640)
-- Name: customers; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.customers (
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



--
-- TOC entry 224 (class 1259 OID 16639)
-- Name: customers_customerid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.customers_customerid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5218 (class 0 OID 0)
-- Dependencies: 224
-- Name: customers_customerid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.customers_customerid_seq OWNED BY public.customers.customerid;


--
-- TOC entry 231 (class 1259 OID 16683)
-- Name: inventory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.inventory (
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



--
-- TOC entry 230 (class 1259 OID 16682)
-- Name: inventory_inventoryid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.inventory_inventoryid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5219 (class 0 OID 0)
-- Dependencies: 230
-- Name: inventory_inventoryid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.inventory_inventoryid_seq OWNED BY public.inventory.inventoryid;


--
-- TOC entry 235 (class 1259 OID 16740)
-- Name: orderdetails; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orderdetails (
    oderdetailid integer NOT NULL,
    orderid integer NOT NULL,
    productid integer NOT NULL,
    quantity integer NOT NULL,
    unitprice numeric(18,2) NOT NULL,
    linetotal numeric(18,2) GENERATED ALWAYS AS (((quantity)::numeric * unitprice)) STORED,
    CONSTRAINT orderdetails_quantity_check CHECK ((quantity > 0)),
    CONSTRAINT orderdetails_unitprice_check CHECK ((unitprice >= (0)::numeric))
);



--
-- TOC entry 234 (class 1259 OID 16739)
-- Name: orderdetails_oderdetailid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orderdetails_oderdetailid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5220 (class 0 OID 0)
-- Dependencies: 234
-- Name: orderdetails_oderdetailid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orderdetails_oderdetailid_seq OWNED BY public.orderdetails.oderdetailid;


--
-- TOC entry 233 (class 1259 OID 16713)
-- Name: orders; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.orders (
    orderid integer NOT NULL,
    ordernumber character varying(50) NOT NULL,
    customerid integer NOT NULL,
    orderdate timestamp without time zone NOT NULL,
    status character varying(50) DEFAULT 'New'::character varying NOT NULL,
    subtotal numeric(18,2) DEFAULT 0 NOT NULL,
    discount numeric(18,2) DEFAULT 0 NOT NULL,
    tax numeric(10,2) DEFAULT 0 NOT NULL,
    totalamount numeric(18,2) DEFAULT 0 NOT NULL,
    CONSTRAINT orders_discount_check CHECK ((discount >= (0)::numeric)),
    CONSTRAINT orders_subtotal_check CHECK ((subtotal >= (0)::numeric)),
    CONSTRAINT orders_tax_check CHECK ((tax >= (0)::numeric)),
    CONSTRAINT orders_totalamount_check CHECK ((totalamount >= (0)::numeric))
);



--
-- TOC entry 232 (class 1259 OID 16712)
-- Name: orders_orderid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.orders_orderid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5221 (class 0 OID 0)
-- Dependencies: 232
-- Name: orders_orderid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.orders_orderid_seq OWNED BY public.orders.orderid;


--
-- TOC entry 237 (class 1259 OID 16755)
-- Name: payments; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.payments (
    paymentid integer NOT NULL,
    orderid integer NOT NULL,
    paymentdate timestamp without time zone NOT NULL,
    amount numeric(18,2) NOT NULL,
    paymentmethod character varying(50) NOT NULL,
    transactionref character varying(200),
    CONSTRAINT payments_amount_check CHECK ((amount >= (0)::numeric))
);



--
-- TOC entry 236 (class 1259 OID 16754)
-- Name: payments_paymentid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.payments_paymentid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5222 (class 0 OID 0)
-- Dependencies: 236
-- Name: payments_paymentid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.payments_paymentid_seq OWNED BY public.payments.paymentid;


--
-- TOC entry 227 (class 1259 OID 16657)
-- Name: products; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.products (
    productid integer NOT NULL,
    sku character varying(50) NOT NULL,
    productname character varying(200) NOT NULL,
    categoryid integer NOT NULL,
    unitprice numeric(18,2) DEFAULT 0 NOT NULL,
    isactive boolean DEFAULT true NOT NULL
);



--
-- TOC entry 226 (class 1259 OID 16656)
-- Name: products_productid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.products_productid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5223 (class 0 OID 0)
-- Dependencies: 226
-- Name: products_productid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.products_productid_seq OWNED BY public.products.productid;


--
-- TOC entry 239 (class 1259 OID 16768)
-- Name: roles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.roles (
    roleid integer NOT NULL,
    rolename character varying(50) NOT NULL,
    description character varying(255),
    issystemrole boolean DEFAULT false NOT NULL,
    createdat timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    updatedat timestamp without time zone
);



--
-- TOC entry 238 (class 1259 OID 16767)
-- Name: roles_roleid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.roles_roleid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5224 (class 0 OID 0)
-- Dependencies: 238
-- Name: roles_roleid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.roles_roleid_seq OWNED BY public.roles.roleid;


--
-- TOC entry 243 (class 1259 OID 16806)
-- Name: userloginhistory; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.userloginhistory (
    loginid bigint NOT NULL,
    userid integer NOT NULL,
    logintime timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    logouttime timestamp without time zone,
    ipaddress character varying(45),
    deviceinfo character varying(255),
    status character varying(20) DEFAULT 'Success'::character varying NOT NULL
);



--
-- TOC entry 242 (class 1259 OID 16805)
-- Name: userloginhistory_loginid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.userloginhistory_loginid_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5225 (class 0 OID 0)
-- Dependencies: 242
-- Name: userloginhistory_loginid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.userloginhistory_loginid_seq OWNED BY public.userloginhistory.loginid;


--
-- TOC entry 245 (class 1259 OID 16819)
-- Name: userpermissions; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.userpermissions (
    permissionid integer NOT NULL,
    userid integer NOT NULL,
    modulename character varying(100) NOT NULL,
    permissionvalue integer NOT NULL,
    createdat timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);



--
-- TOC entry 244 (class 1259 OID 16818)
-- Name: userpermissions_permissionid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.userpermissions_permissionid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5226 (class 0 OID 0)
-- Dependencies: 244
-- Name: userpermissions_permissionid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.userpermissions_permissionid_seq OWNED BY public.userpermissions.permissionid;


--
-- TOC entry 247 (class 1259 OID 16831)
-- Name: userprofiles; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.userprofiles (
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



--
-- TOC entry 246 (class 1259 OID 16830)
-- Name: userprofiles_profileid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.userprofiles_profileid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5227 (class 0 OID 0)
-- Dependencies: 246
-- Name: userprofiles_profileid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.userprofiles_profileid_seq OWNED BY public.userprofiles.profileid;


--
-- TOC entry 241 (class 1259 OID 16783)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
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



--
-- TOC entry 240 (class 1259 OID 16782)
-- Name: users_userid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.users_userid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5228 (class 0 OID 0)
-- Dependencies: 240
-- Name: users_userid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.users_userid_seq OWNED BY public.users.userid;


--
-- TOC entry 229 (class 1259 OID 16674)
-- Name: warehouse; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.warehouse (
    warehouseid integer NOT NULL,
    warehousename character varying(200) NOT NULL,
    location character varying(200)
);



--
-- TOC entry 228 (class 1259 OID 16673)
-- Name: warehouse_warehouseid_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.warehouse_warehouseid_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;



--
-- TOC entry 5229 (class 0 OID 0)
-- Dependencies: 228
-- Name: warehouse_warehouseid_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.warehouse_warehouseid_seq OWNED BY public.warehouse.warehouseid;


--
-- TOC entry 4932 (class 2604 OID 16621)
-- Name: auditlogs auditid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditlogs ALTER COLUMN auditid SET DEFAULT nextval('public.auditlogs_auditid_seq'::regclass);


--
-- TOC entry 4934 (class 2604 OID 16634)
-- Name: categories categoryid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories ALTER COLUMN categoryid SET DEFAULT nextval('public.categories_categoryid_seq'::regclass);


--
-- TOC entry 4935 (class 2604 OID 16643)
-- Name: customers customerid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers ALTER COLUMN customerid SET DEFAULT nextval('public.customers_customerid_seq'::regclass);


--
-- TOC entry 4941 (class 2604 OID 16686)
-- Name: inventory inventoryid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory ALTER COLUMN inventoryid SET DEFAULT nextval('public.inventory_inventoryid_seq'::regclass);


--
-- TOC entry 4957 (class 2604 OID 16743)
-- Name: orderdetails oderdetailid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orderdetails ALTER COLUMN oderdetailid SET DEFAULT nextval('public.orderdetails_oderdetailid_seq'::regclass);


--
-- TOC entry 4951 (class 2604 OID 16716)
-- Name: orders orderid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders ALTER COLUMN orderid SET DEFAULT nextval('public.orders_orderid_seq'::regclass);


--
-- TOC entry 4959 (class 2604 OID 16758)
-- Name: payments paymentid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments ALTER COLUMN paymentid SET DEFAULT nextval('public.payments_paymentid_seq'::regclass);


--
-- TOC entry 4937 (class 2604 OID 16660)
-- Name: products productid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products ALTER COLUMN productid SET DEFAULT nextval('public.products_productid_seq'::regclass);


--
-- TOC entry 4960 (class 2604 OID 16771)
-- Name: roles roleid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles ALTER COLUMN roleid SET DEFAULT nextval('public.roles_roleid_seq'::regclass);


--
-- TOC entry 4966 (class 2604 OID 16809)
-- Name: userloginhistory loginid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userloginhistory ALTER COLUMN loginid SET DEFAULT nextval('public.userloginhistory_loginid_seq'::regclass);


--
-- TOC entry 4969 (class 2604 OID 16822)
-- Name: userpermissions permissionid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userpermissions ALTER COLUMN permissionid SET DEFAULT nextval('public.userpermissions_permissionid_seq'::regclass);


--
-- TOC entry 4971 (class 2604 OID 16834)
-- Name: userprofiles profileid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userprofiles ALTER COLUMN profileid SET DEFAULT nextval('public.userprofiles_profileid_seq'::regclass);


--
-- TOC entry 4963 (class 2604 OID 16786)
-- Name: users userid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN userid SET DEFAULT nextval('public.users_userid_seq'::regclass);


--
-- TOC entry 4940 (class 2604 OID 16677)
-- Name: warehouse warehouseid; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse ALTER COLUMN warehouseid SET DEFAULT nextval('public.warehouse_warehouseid_seq'::regclass);


--
-- TOC entry 5183 (class 0 OID 16618)
-- Dependencies: 221
-- Data for Name: auditlogs; Type: TABLE DATA; Schema: public; Owner: postgres
--



--
-- TOC entry 5185 (class 0 OID 16631)
-- Dependencies: 223
-- Data for Name: categories; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.categories (categoryid, categoryname) VALUES ('65', 'Computer');
INSERT INTO public.categories (categoryid, categoryname) VALUES ('66', 'Laptop');
INSERT INTO public.categories (categoryid, categoryname) VALUES ('68', 'Mobile');
INSERT INTO public.categories (categoryid, categoryname) VALUES ('71', 'Samsung');


--
-- TOC entry 5187 (class 0 OID 16640)
-- Dependencies: 225
-- Data for Name: customers; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100003', 'CUST-000001', 'Alamgir Kabir', '01712706040', 'alamgirkabir.wave@gmail.com', 'Dhaka', '2025-11-19 15:29:05.839915', '01841338354', 'Flat # A5, Block-R, House # 48, Block : R/S, Nurjahan Road, Mohammadpur, Dhaka', 'Dhaka', '1207', 'Retail', '123456789101', '', 'Test for Delete', 'He is the Regula customer', 't', 'Admin', 'Admin', '2025-11-19 16:10:21.005352');
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100005', 'CUST-000002', 'Hasan Mahmud', '01711000002', 'hasan@example.com', 'Dhaka', '2025-11-19 16:14:17.216667', '01841000002', 'Mirpur DOHS, Dhaka', 'Dhaka', '1216', 'Retail', '987654321012', NULL, 'Mr. Jui', 'New customer', 't', 'Admin', NULL, NULL);
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100006', 'CUST-000003', 'Shamim Ahmed', '01711000003', 'shamim@example.com', 'Chattogram', '2025-11-19 16:14:17.216667', '01841000003', 'Noman Society, Agrabad', 'Chattogram', '4000', 'Dealer', '998877665544', NULL, 'Mr. Imtiaz', 'Good relationship', 't', 'Admin', NULL, NULL);
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100007', 'CUST-000004', 'Runa Akter', '01711000004', 'runa@example.com', 'Sylhet', '2025-11-19 16:14:17.216667', '01841000004', 'Zindabazar, Sylhet', 'Sylhet', '3100', 'Retail', '112233445566', NULL, 'Ms. Lima', 'Frequent buyer', 't', 'Admin', NULL, NULL);
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100008', 'CUST-000005', 'Fahim Khan', '01711000005', 'fahim@example.com', 'Khulna', '2025-11-19 16:14:17.216667', '01841000005', 'Sonadanga, Khulna', 'Khulna', '9000', 'Dealer', '556677889900', '123456789', 'Mr. Rashed', 'Corporate client', 't', 'Admin', 'Admin', '2025-11-20 05:11:40.698994');
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100009', 'CUST-000006', 'Jannat Ara', '01711000006', 'jannat@example.com', 'Rajshahi', '2025-11-19 16:14:17.216667', '01841000006', 'Shaheb Bazar, Rajshahi', 'Rajshahi', '6000', 'Retail', '778899001122', NULL, 'Ms. Asha', 'Occasional buyer', 't', 'Admin', NULL, NULL);
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100010', 'CUST-000007', 'Rahim Uddin', '01711000007', 'rahim@example.com', 'Barishal', '2025-11-19 16:14:17.216667', '01841000007', 'Band Road, Barishal', 'Barishal', '8200', 'Dealer', '445566778899', NULL, 'Mr. Rubel', 'Local dealer', 't', 'Admin', NULL, NULL);
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100011', 'CUST-000008', 'Farzana Rahman', '01711000008', 'farzana@example.com', 'Rangpur', '2025-11-19 16:14:17.216667', '01841000008', 'Rangpur Sadar, Rangpur', 'Rangpur', '5400', 'VIP', '667788990011', NULL, 'Ms. Priya', 'High-value customer', 't', 'Admin', NULL, NULL);
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100013', 'CUST-000010', 'Sumaiya Islam', '01711000010', 'sumaiya@example.com', 'Narayanganj', '2025-11-19 16:14:17.216667', '01841000010', 'Fatullah, Narayanganj', 'Narayanganj', '1400', 'Retail', '223344556677', NULL, 'Ms. Shila', 'New customer', 't', 'Admin', NULL, NULL);
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100014', 'CUST-000011', 'Rezaul Karim', '01711000011', 'rezaul@example.com', 'Mymensingh', '2025-11-19 16:14:17.216667', '01841000011', 'Town Hall, Mymensingh', 'Mymensingh', '2200', 'Retail', '990011223344', '', 'Mr. Adnan', 'Monthly buyer', 't', 'Admin', 'Admin', '2025-11-20 05:11:19.75076');
INSERT INTO public.customers (customerid, customercode, fullname, contactphone, email, region, createddate, alternatephone, address, city, postalcode, customertype, nid, taxnumber, contactperson, notes, isactive, createdby, updatedby, updateddate) VALUES ('100016', 'CUST-100015', 'Alamgir Kabir', '01712706041', '', '', '2025-11-20 07:48:35.469217', '', '', 'খুলনা', '', 'Retail', '12345678', '123456', 'Fahim Khan', 'এনআইডি ও ট্যাক্স ভ্যালিডেশন দিতে হবে', 't', 'Admin', NULL, '2025-11-20 07:50:49.675525');


--
-- TOC entry 5193 (class 0 OID 16683)
-- Dependencies: 231
-- Data for Name: inventory; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.inventory (inventoryid, productid, warehouseid, stockqty, lastupdate, purchaseprice, salesprice, avgcost, reorderlevel, safetystock, maxstock, batchno, expirydate, unitofmeasureid, currencycode, valuationmethod, createdat, createdby, updatedat, updatedby, isactive) VALUES ('50013', '8', '1', '2', '2025-11-19 11:21:57.186094', '50000.0000', '0.0000', NULL, '0', '0', NULL, NULL, NULL, NULL, 'USD', 'AVG', '2025-11-19 11:01:53.286535', NULL, NULL, NULL, 't');
INSERT INTO public.inventory (inventoryid, productid, warehouseid, stockqty, lastupdate, purchaseprice, salesprice, avgcost, reorderlevel, safetystock, maxstock, batchno, expirydate, unitofmeasureid, currencycode, valuationmethod, createdat, createdby, updatedat, updatedby, isactive) VALUES ('50015', '7', '1', '2', '2025-11-20 19:42:19.520481', '0.0000', '0.0000', NULL, '0', '0', NULL, NULL, NULL, NULL, 'USD', 'AVG', '2025-11-21 01:37:21.383933', NULL, NULL, NULL, 't');
INSERT INTO public.inventory (inventoryid, productid, warehouseid, stockqty, lastupdate, purchaseprice, salesprice, avgcost, reorderlevel, safetystock, maxstock, batchno, expirydate, unitofmeasureid, currencycode, valuationmethod, createdat, createdby, updatedat, updatedby, isactive) VALUES ('50014', '11', '2', '2', '2025-11-20 19:42:23.484822', '50000.0000', '0.0000', NULL, '0', '0', NULL, NULL, NULL, NULL, 'USD', 'AVG', '2025-11-19 11:22:42.560897', NULL, NULL, NULL, 't');


--
-- TOC entry 5197 (class 0 OID 16740)
-- Dependencies: 235
-- Data for Name: orderdetails; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.orderdetails (oderdetailid, orderid, productid, quantity, unitprice) VALUES ('1', '200031', '8', '1', '28000.00');
INSERT INTO public.orderdetails (oderdetailid, orderid, productid, quantity, unitprice) VALUES ('2', '200031', '11', '3', '17000.00');
INSERT INTO public.orderdetails (oderdetailid, orderid, productid, quantity, unitprice) VALUES ('4', '200032', '7', '1', '72000.00');
INSERT INTO public.orderdetails (oderdetailid, orderid, productid, quantity, unitprice) VALUES ('5', '200032', '11', '1', '15000.00');
INSERT INTO public.orderdetails (oderdetailid, orderid, productid, quantity, unitprice) VALUES ('6', '200032', '14', '2', '19999.00');
INSERT INTO public.orderdetails (oderdetailid, orderid, productid, quantity, unitprice) VALUES ('7', '200031', '13', '3', '99000.00');


--
-- TOC entry 5195 (class 0 OID 16713)
-- Dependencies: 233
-- Data for Name: orders; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.orders (orderid, ordernumber, customerid, orderdate, status, subtotal, discount, tax, totalamount) VALUES ('200032', '20251120-0001', '100005', '2025-11-19 00:00:00', 'Pending', '15000.00', '0.00', '0.00', '15000.00');
INSERT INTO public.orders (orderid, ordernumber, customerid, orderdate, status, subtotal, discount, tax, totalamount) VALUES ('200031', '001', '100016', '2025-11-20 00:00:00', 'Pending', '10000.00', '10.00', '1.00', '9991.00');


--
-- TOC entry 5199 (class 0 OID 16755)
-- Dependencies: 237
-- Data for Name: payments; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.payments (paymentid, orderid, paymentdate, amount, paymentmethod, transactionref) VALUES ('2', '200032', '2025-11-21 00:00:00', '3000.00', 'Card', '2');


--
-- TOC entry 5189 (class 0 OID 16657)
-- Dependencies: 227
-- Data for Name: products; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('10', 'LAP-6601', 'Samsung Smart TV 43 Inch', '66', '55000.00', 't');
INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('11', 'SAM-7101', '6.5 Inch Android 20 Phone', '71', '15000.00', 't');
INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('12', 'LAP-6602', 'Dell Laptop', '66', '51000.00', 't');
INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('13', 'COM-6502', 'Core I Seven, Dell', '65', '99000.00', 't');
INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('14', 'MOB-6801', 'Techno 14', '68', '19999.00', 't');
INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('15', 'LAP-6603', 'Desktop Coputer', '66', '99999.00', 't');
INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('16', 'COM-6503', 'Desktop Computer', '65', '99999.00', 't');
INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('8', 'COM-6504', 'HP Laptop 14th Generation', '65', '28000.00', 't');
INSERT INTO public.products (productid, sku, productname, categoryid, unitprice, isactive) VALUES ('7', 'LAP-6604', 'Dell Inspiron Laptop 13th Gen', '66', '72000.00', 'f');


--
-- TOC entry 5201 (class 0 OID 16768)
-- Dependencies: 239
-- Data for Name: roles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) VALUES ('1', 'Administrator', 'Full access', 't', '2025-11-13 17:25:57.673333', '2025-11-13 20:45:34.986667');
INSERT INTO public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) VALUES ('2', 'Manager', 'Can oversee operations and manage user activities.', 'f', '2025-11-13 17:25:57.673333', NULL);
INSERT INTO public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) VALUES ('3', 'Data Analyst', 'Can view and analyze data reports and dashboards.', 't', '2025-11-13 17:25:57.673333', '2025-11-13 20:45:58.943333');
INSERT INTO public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) VALUES ('4', 'Accountant', 'Responsible for managing financial transactions and reports.', 'f', '2025-11-13 17:25:57.673333', NULL);
INSERT INTO public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) VALUES ('6', 'Loan Officer', 'Create Loan', 'f', '2025-11-13 20:00:45.313333', '2025-11-13 20:00:45.313333');
INSERT INTO public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) VALUES ('7', 'Area Manager', 'safws asfds', 'f', '2025-11-13 20:14:51.126667', '2025-11-13 20:14:51.126667');
INSERT INTO public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) VALUES ('8', 'Regional Manager', 'Regional manger can only ready Data', 'f', '2025-11-13 20:27:39.276667', '2025-11-13 20:27:39.276667');
INSERT INTO public.roles (roleid, rolename, description, issystemrole, createdat, updatedat) VALUES ('9', 'CDO', 'sdfsd fdsfs', 'f', '2025-11-20 17:34:56.88174', '2025-11-20 17:39:04.419635');


--
-- TOC entry 5205 (class 0 OID 16806)
-- Dependencies: 243
-- Data for Name: userloginhistory; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('1', '1', '2025-11-18 10:30:07.186667', '2025-11-18 10:32:16.363333', '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('2', '1', '2025-11-18 10:32:20.686667', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('3', '1', '2025-11-18 10:36:34.476667', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('4', '1', '2025-11-18 10:39:48.623333', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('5', '1', '2025-11-18 10:40:03.23', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('6', '1', '2025-11-18 10:41:57.073333', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('7', '1', '2025-11-18 10:43:16.083333', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('8', '1', '2025-11-18 10:43:17.18', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('9', '1', '2025-11-18 10:43:17.88', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('10', '1', '2025-11-18 10:43:18.88', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('11', '1', '2025-11-18 10:43:50.636667', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('12', '1', '2025-11-18 10:43:51.196667', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('13', '1', '2025-11-18 10:48:31.133333', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('14', '1', '2025-11-18 10:50:15.706667', NULL, '192.168.0.207', 'Windows 10', 'Success');
INSERT INTO public.userloginhistory (loginid, userid, logintime, logouttime, ipaddress, deviceinfo, status) VALUES ('15', '1', '2025-11-18 10:52:21.896667', NULL, '192.168.0.207', 'Windows 10', 'Success');


--
-- TOC entry 5207 (class 0 OID 16819)
-- Dependencies: 245
-- Data for Name: userpermissions; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('1', '1', 'Users', '15', '2025-11-16 17:06:17.240023');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('2', '1', 'Auth', '15', '2025-11-16 17:11:32.67006');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('3', '3', 'Auth', '15', '2025-11-16 17:17:57.400763');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('4', '3', 'Users', '7', '2025-11-16 17:30:24.502772');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('5', '3', 'Roles', '15', '2025-11-16 17:17:57.416752');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('6', '3', 'Permissions', '15', '2025-11-16 17:17:57.420373');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('7', '3', 'UserProfiles', '15', '2025-11-16 17:17:57.426356');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('8', '3', 'UserLoginHistory', '15', '2025-11-16 17:17:57.433529');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('9', '3', 'AuditLogs', '15', '2025-11-16 17:17:57.438009');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('10', '3', 'AdminDashboard', '15', '2025-11-16 17:17:57.442202');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('11', '3', 'ShopDashboard', '15', '2025-11-16 17:17:57.448134');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('12', '3', 'UserDashboard', '15', '2025-11-16 17:17:57.454316');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('13', '3', 'ShopManagement', '15', '2025-11-16 17:17:57.457439');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('14', '3', 'SalesManagement', '15', '2025-11-16 17:17:57.460482');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('15', '3', 'InventoryManagement', '15', '2025-11-16 17:17:57.468075');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('16', '3', 'CustomerManagement', '15', '2025-11-16 17:17:57.47711');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('17', '3', 'LoanManagement', '15', '2025-11-16 17:17:57.483383');
INSERT INTO public.userpermissions (permissionid, userid, modulename, permissionvalue, createdat) VALUES ('18', '3', 'PaymentManagement', '15', '2025-11-16 17:17:57.48508');


--
-- TOC entry 5209 (class 0 OID 16831)
-- Dependencies: 247
-- Data for Name: userprofiles; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.userprofiles (profileid, userid, address, city, country, dateofbirth, gender, profilepictureurl, createdat, updatedat) VALUES ('5', '1', 'House #12, Road #5, Dhanmondi', 'Dhaka', 'Bangladesh', '1990-05-12', 'Male', 'https://example.com/profiles/alamgir.jpg', '2025-11-16 09:44:53.756667', NULL);
INSERT INTO public.userprofiles (profileid, userid, address, city, country, dateofbirth, gender, profilepictureurl, createdat, updatedat) VALUES ('8', '1', 'Flat # A5, Block-R, House # 48, Block : R/S, Nurjahan Road, Mohammadpur, Dhaka', 'Dhaka', 'Bangladesh', '1979-11-06', 'Male', 'uploads/profile_pics\\user_1.JPG', '2025-11-16 13:03:44.30145', '2025-11-20 20:45:54.412014');


--
-- TOC entry 5203 (class 0 OID 16783)
-- Dependencies: 241
-- Data for Name: users; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.users (userid, username, fullname, email, phonenumber, passwordhash, roleid, isactive, lastlogin, createdat, updatedat) VALUES ('1', 'Alamgir', 'Alamgir Kabir', 'alamgirfrombd@gmail.com', '01712706040', 'hashed_password_here', '7', 't', NULL, '2025-11-15 19:51:59.07', '2025-11-15 21:41:18.606979');
INSERT INTO public.users (userid, username, fullname, email, phonenumber, passwordhash, roleid, isactive, lastlogin, createdat, updatedat) VALUES ('4', 'Beauty', 'Hafiza Khatun', 'hafiza@gmail.com', '01931670959', '$2b$12$tUfZ77p2tI7uARoatpCylenZq4xo3hOCL/3aXMeS77E7MNsNjIhtS', '7', 't', NULL, '2025-11-15 21:35:59.050281', '2025-11-15 21:35:59.050281');
INSERT INTO public.users (userid, username, fullname, email, phonenumber, passwordhash, roleid, isactive, lastlogin, createdat, updatedat) VALUES ('5', 'Rifat', 'Rifat Muzakkir', 'rifat@gmail.com', '01841338354', '$2b$12$O1vBDVBjaXX9Qo3aaI30MeTNYvyvi54eT62wzq7s1HRZm0z5jXnu6', '3', 't', NULL, '2025-11-15 21:42:10.669953', '2025-11-16 09:10:16.972464');
INSERT INTO public.users (userid, username, fullname, email, phonenumber, passwordhash, roleid, isactive, lastlogin, createdat, updatedat) VALUES ('3', 'abony', 'Promity Abony', 'abon@gmail.com', '01711706040', 'Alamgir@123', '1', 't', NULL, '2025-11-15 20:45:39.718651', '2025-11-20 17:51:21.842912');


--
-- TOC entry 5191 (class 0 OID 16674)
-- Dependencies: 229
-- Data for Name: warehouse; Type: TABLE DATA; Schema: public; Owner: postgres
--

INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('1', 'Central Warehouse', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('2', 'North Hub', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('3', 'South Hub', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('4', 'East Depot', 'Sylhet');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('5', 'West Depot', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('6', 'City Storage 1', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('7', 'City Storage 2', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('10', 'City Storage 5', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('11', 'Main Distribution Center', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('12', 'Backup Warehouse', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('13', 'Temporary Storage 1', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('14', 'Temporary Storage 2', 'Sylhet');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('15', 'Temporary Storage 3', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('16', 'North-East Storage', 'Sylhet');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('17', 'North-West Storage', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('18', 'South-East Storage', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('19', 'South-West Storage', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('20', 'Industrial Warehouse 1', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('21', 'Industrial Warehouse 2', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('22', 'Industrial Warehouse 3', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('23', 'Industrial Warehouse 4', 'Sylhet');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('24', 'Industrial Warehouse 5', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('25', 'Standard Depot 1', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('26', 'Standard Depot 2', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('27', 'Standard Depot 3', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('28', 'Standard Depot 4', 'Sylhet');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('29', 'Standard Depot 5', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('30', 'Logistics Hub 1', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('31', 'Logistics Hub 2', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('32', 'Logistics Hub 3', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('33', 'Logistics Hub 4', 'Sylhet');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('34', 'Logistics Hub 5', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('35', 'Warehouse Alpha', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('36', 'Warehouse Beta', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('37', 'Warehouse Gamma', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('38', 'Warehouse Delta', 'Sylhet');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('39', 'Warehouse Epsilon', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('40', 'Regional Hub 1', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('41', 'Regional Hub 2', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('42', 'Regional Hub 3', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('43', 'Regional Hub 4', 'Sylhet');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('44', 'Regional Hub 5', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('45', 'City Hub A', 'Dhaka');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('46', 'City Hub B', 'Chittagong');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('47', 'City Hub C', 'Khulna');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('49', 'Jhenaidah_Alamgir', 'Rajshahi');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('50', 'Power House', 'Chuadanga');
INSERT INTO public.warehouse (warehouseid, warehousename, location) VALUES ('9', 'City Storage 50', 'Sylhet');


--
-- TOC entry 5230 (class 0 OID 0)
-- Dependencies: 220
-- Name: auditlogs_auditid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.auditlogs_auditid_seq', 1, false);


--
-- TOC entry 5231 (class 0 OID 0)
-- Dependencies: 222
-- Name: categories_categoryid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.categories_categoryid_seq', 71, true);


--
-- TOC entry 5232 (class 0 OID 0)
-- Dependencies: 224
-- Name: customers_customerid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.customers_customerid_seq', 100016, true);


--
-- TOC entry 5233 (class 0 OID 0)
-- Dependencies: 230
-- Name: inventory_inventoryid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.inventory_inventoryid_seq', 50015, true);


--
-- TOC entry 5234 (class 0 OID 0)
-- Dependencies: 234
-- Name: orderdetails_oderdetailid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orderdetails_oderdetailid_seq', 7, true);


--
-- TOC entry 5235 (class 0 OID 0)
-- Dependencies: 232
-- Name: orders_orderid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.orders_orderid_seq', 200032, true);


--
-- TOC entry 5236 (class 0 OID 0)
-- Dependencies: 236
-- Name: payments_paymentid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.payments_paymentid_seq', 2, true);


--
-- TOC entry 5237 (class 0 OID 0)
-- Dependencies: 226
-- Name: products_productid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.products_productid_seq', 16, true);


--
-- TOC entry 5238 (class 0 OID 0)
-- Dependencies: 238
-- Name: roles_roleid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.roles_roleid_seq', 10, true);


--
-- TOC entry 5239 (class 0 OID 0)
-- Dependencies: 242
-- Name: userloginhistory_loginid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.userloginhistory_loginid_seq', 15, true);


--
-- TOC entry 5240 (class 0 OID 0)
-- Dependencies: 244
-- Name: userpermissions_permissionid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.userpermissions_permissionid_seq', 18, true);


--
-- TOC entry 5241 (class 0 OID 0)
-- Dependencies: 246
-- Name: userprofiles_profileid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.userprofiles_profileid_seq', 8, true);


--
-- TOC entry 5242 (class 0 OID 0)
-- Dependencies: 240
-- Name: users_userid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.users_userid_seq', 5, true);


--
-- TOC entry 5243 (class 0 OID 0)
-- Dependencies: 228
-- Name: warehouse_warehouseid_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.warehouse_warehouseid_seq', 50, true);


--
-- TOC entry 4982 (class 2606 OID 16629)
-- Name: auditlogs auditlogs_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditlogs
    ADD CONSTRAINT auditlogs_pkey PRIMARY KEY (auditid);


--
-- TOC entry 4984 (class 2606 OID 16638)
-- Name: categories categories_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.categories
    ADD CONSTRAINT categories_pkey PRIMARY KEY (categoryid);


--
-- TOC entry 4986 (class 2606 OID 16655)
-- Name: customers customers_customercode_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_customercode_key UNIQUE (customercode);


--
-- TOC entry 4988 (class 2606 OID 16653)
-- Name: customers customers_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.customers
    ADD CONSTRAINT customers_pkey PRIMARY KEY (customerid);


--
-- TOC entry 4996 (class 2606 OID 16709)
-- Name: inventory inventory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_pkey PRIMARY KEY (inventoryid);


--
-- TOC entry 4998 (class 2606 OID 16711)
-- Name: inventory inventory_productid_warehouseid_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT inventory_productid_warehouseid_key UNIQUE (productid, warehouseid);


--
-- TOC entry 5004 (class 2606 OID 16753)
-- Name: orderdetails orderdetails_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orderdetails
    ADD CONSTRAINT orderdetails_pkey PRIMARY KEY (oderdetailid);


--
-- TOC entry 5000 (class 2606 OID 16738)
-- Name: orders orders_ordernumber_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_ordernumber_key UNIQUE (ordernumber);


--
-- TOC entry 5002 (class 2606 OID 16736)
-- Name: orders orders_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT orders_pkey PRIMARY KEY (orderid);


--
-- TOC entry 5006 (class 2606 OID 16766)
-- Name: payments payments_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT payments_pkey PRIMARY KEY (paymentid);


--
-- TOC entry 4990 (class 2606 OID 16670)
-- Name: products products_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_pkey PRIMARY KEY (productid);


--
-- TOC entry 4992 (class 2606 OID 16672)
-- Name: products products_sku_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT products_sku_key UNIQUE (sku);


--
-- TOC entry 5008 (class 2606 OID 16779)
-- Name: roles roles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_pkey PRIMARY KEY (roleid);


--
-- TOC entry 5010 (class 2606 OID 16781)
-- Name: roles roles_rolename_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.roles
    ADD CONSTRAINT roles_rolename_key UNIQUE (rolename);


--
-- TOC entry 5018 (class 2606 OID 16817)
-- Name: userloginhistory userloginhistory_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userloginhistory
    ADD CONSTRAINT userloginhistory_pkey PRIMARY KEY (loginid);


--
-- TOC entry 5020 (class 2606 OID 16829)
-- Name: userpermissions userpermissions_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userpermissions
    ADD CONSTRAINT userpermissions_pkey PRIMARY KEY (permissionid);


--
-- TOC entry 5022 (class 2606 OID 16842)
-- Name: userprofiles userprofiles_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userprofiles
    ADD CONSTRAINT userprofiles_pkey PRIMARY KEY (profileid);


--
-- TOC entry 5012 (class 2606 OID 16804)
-- Name: users users_email_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_email_key UNIQUE (email);


--
-- TOC entry 5014 (class 2606 OID 16800)
-- Name: users users_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (userid);


--
-- TOC entry 5016 (class 2606 OID 16802)
-- Name: users users_username_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_username_key UNIQUE (username);


--
-- TOC entry 4994 (class 2606 OID 16681)
-- Name: warehouse warehouse_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.warehouse
    ADD CONSTRAINT warehouse_pkey PRIMARY KEY (warehouseid);


--
-- TOC entry 5023 (class 2606 OID 16843)
-- Name: auditlogs fk_auditlogs_userid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.auditlogs
    ADD CONSTRAINT fk_auditlogs_userid FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- TOC entry 5025 (class 2606 OID 16848)
-- Name: inventory fk_inventory_productsid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT fk_inventory_productsid FOREIGN KEY (productid) REFERENCES public.products(productid);


--
-- TOC entry 5026 (class 2606 OID 16853)
-- Name: inventory fk_inventory_warehouseid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.inventory
    ADD CONSTRAINT fk_inventory_warehouseid FOREIGN KEY (warehouseid) REFERENCES public.warehouse(warehouseid);


--
-- TOC entry 5028 (class 2606 OID 16858)
-- Name: orderdetails fk_orderdetails_orderid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orderdetails
    ADD CONSTRAINT fk_orderdetails_orderid FOREIGN KEY (orderid) REFERENCES public.orders(orderid) ON DELETE CASCADE;


--
-- TOC entry 5029 (class 2606 OID 16863)
-- Name: orderdetails fk_orderdetails_productid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orderdetails
    ADD CONSTRAINT fk_orderdetails_productid FOREIGN KEY (productid) REFERENCES public.products(productid);


--
-- TOC entry 5027 (class 2606 OID 16868)
-- Name: orders fk_orders_customerid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.orders
    ADD CONSTRAINT fk_orders_customerid FOREIGN KEY (customerid) REFERENCES public.customers(customerid);


--
-- TOC entry 5030 (class 2606 OID 16873)
-- Name: payments fk_payments_orders; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.payments
    ADD CONSTRAINT fk_payments_orders FOREIGN KEY (orderid) REFERENCES public.orders(orderid);


--
-- TOC entry 5024 (class 2606 OID 16878)
-- Name: products fk_products_category; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.products
    ADD CONSTRAINT fk_products_category FOREIGN KEY (categoryid) REFERENCES public.categories(categoryid);


--
-- TOC entry 5032 (class 2606 OID 16883)
-- Name: userloginhistory fk_userloginhistory_userid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userloginhistory
    ADD CONSTRAINT fk_userloginhistory_userid FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- TOC entry 5033 (class 2606 OID 16888)
-- Name: userpermissions fk_userpermissions_userid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userpermissions
    ADD CONSTRAINT fk_userpermissions_userid FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- TOC entry 5034 (class 2606 OID 16893)
-- Name: userprofiles fk_userprofiles_userid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.userprofiles
    ADD CONSTRAINT fk_userprofiles_userid FOREIGN KEY (userid) REFERENCES public.users(userid);


--
-- TOC entry 5031 (class 2606 OID 16898)
-- Name: users fk_users_roleid; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT fk_users_roleid FOREIGN KEY (roleid) REFERENCES public.roles(roleid);


-- Completed on 2025-11-21 15:51:20

--
-- PostgreSQL database dump complete
--

