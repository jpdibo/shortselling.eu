--
-- PostgreSQL database dump
--

-- Dumped from database version 17.5
-- Dumped by pg_dump version 17.5

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'WIN1252';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: analytics_cache; Type: TABLE; Schema: public; Owner: jpdib
--

CREATE TABLE public.analytics_cache (
    id integer NOT NULL,
    cache_key character varying(200) NOT NULL,
    cache_data text NOT NULL,
    expires_at timestamp without time zone NOT NULL,
    created_at timestamp without time zone
);


ALTER TABLE public.analytics_cache OWNER TO jpdib;

--
-- Name: analytics_cache_id_seq; Type: SEQUENCE; Schema: public; Owner: jpdib
--

CREATE SEQUENCE public.analytics_cache_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.analytics_cache_id_seq OWNER TO jpdib;

--
-- Name: analytics_cache_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jpdib
--

ALTER SEQUENCE public.analytics_cache_id_seq OWNED BY public.analytics_cache.id;


--
-- Name: companies; Type: TABLE; Schema: public; Owner: jpdib
--

CREATE TABLE public.companies (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    isin character varying(12),
    country_id integer NOT NULL,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.companies OWNER TO jpdib;

--
-- Name: companies_id_seq; Type: SEQUENCE; Schema: public; Owner: jpdib
--

CREATE SEQUENCE public.companies_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.companies_id_seq OWNER TO jpdib;

--
-- Name: companies_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jpdib
--

ALTER SEQUENCE public.companies_id_seq OWNED BY public.companies.id;


--
-- Name: countries; Type: TABLE; Schema: public; Owner: jpdib
--

CREATE TABLE public.countries (
    id integer NOT NULL,
    code character varying(2) NOT NULL,
    name character varying(100) NOT NULL,
    flag character varying(10) NOT NULL,
    priority character varying(10),
    url character varying(500) NOT NULL,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.countries OWNER TO jpdib;

--
-- Name: countries_id_seq; Type: SEQUENCE; Schema: public; Owner: jpdib
--

CREATE SEQUENCE public.countries_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.countries_id_seq OWNER TO jpdib;

--
-- Name: countries_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jpdib
--

ALTER SEQUENCE public.countries_id_seq OWNED BY public.countries.id;


--
-- Name: managers; Type: TABLE; Schema: public; Owner: jpdib
--

CREATE TABLE public.managers (
    id integer NOT NULL,
    name character varying(200) NOT NULL,
    slug character varying(200),
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.managers OWNER TO jpdib;

--
-- Name: managers_id_seq; Type: SEQUENCE; Schema: public; Owner: jpdib
--

CREATE SEQUENCE public.managers_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.managers_id_seq OWNER TO jpdib;

--
-- Name: managers_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jpdib
--

ALTER SEQUENCE public.managers_id_seq OWNED BY public.managers.id;


--
-- Name: scraping_logs; Type: TABLE; Schema: public; Owner: jpdib
--

CREATE TABLE public.scraping_logs (
    id integer NOT NULL,
    country_id integer NOT NULL,
    status character varying(20) NOT NULL,
    records_scraped integer,
    error_message text,
    started_at timestamp without time zone,
    completed_at timestamp without time zone
);


ALTER TABLE public.scraping_logs OWNER TO jpdib;

--
-- Name: scraping_logs_id_seq; Type: SEQUENCE; Schema: public; Owner: jpdib
--

CREATE SEQUENCE public.scraping_logs_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.scraping_logs_id_seq OWNER TO jpdib;

--
-- Name: scraping_logs_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jpdib
--

ALTER SEQUENCE public.scraping_logs_id_seq OWNED BY public.scraping_logs.id;


--
-- Name: short_positions; Type: TABLE; Schema: public; Owner: jpdib
--

CREATE TABLE public.short_positions (
    id integer NOT NULL,
    date timestamp without time zone NOT NULL,
    company_id integer NOT NULL,
    manager_id integer NOT NULL,
    country_id integer NOT NULL,
    position_size double precision NOT NULL,
    is_active boolean,
    source_url character varying(500),
    raw_data text,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.short_positions OWNER TO jpdib;

--
-- Name: short_positions_id_seq; Type: SEQUENCE; Schema: public; Owner: jpdib
--

CREATE SEQUENCE public.short_positions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.short_positions_id_seq OWNER TO jpdib;

--
-- Name: short_positions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jpdib
--

ALTER SEQUENCE public.short_positions_id_seq OWNED BY public.short_positions.id;


--
-- Name: subscriptions; Type: TABLE; Schema: public; Owner: jpdib
--

CREATE TABLE public.subscriptions (
    id integer NOT NULL,
    first_name character varying(100) NOT NULL,
    email character varying(200) NOT NULL,
    frequency character varying(20),
    countries text,
    is_active boolean,
    created_at timestamp without time zone,
    updated_at timestamp without time zone
);


ALTER TABLE public.subscriptions OWNER TO jpdib;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE; Schema: public; Owner: jpdib
--

CREATE SEQUENCE public.subscriptions_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.subscriptions_id_seq OWNER TO jpdib;

--
-- Name: subscriptions_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: jpdib
--

ALTER SEQUENCE public.subscriptions_id_seq OWNED BY public.subscriptions.id;


--
-- Name: analytics_cache id; Type: DEFAULT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.analytics_cache ALTER COLUMN id SET DEFAULT nextval('public.analytics_cache_id_seq'::regclass);


--
-- Name: companies id; Type: DEFAULT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.companies ALTER COLUMN id SET DEFAULT nextval('public.companies_id_seq'::regclass);


--
-- Name: countries id; Type: DEFAULT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.countries ALTER COLUMN id SET DEFAULT nextval('public.countries_id_seq'::regclass);


--
-- Name: managers id; Type: DEFAULT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.managers ALTER COLUMN id SET DEFAULT nextval('public.managers_id_seq'::regclass);


--
-- Name: scraping_logs id; Type: DEFAULT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.scraping_logs ALTER COLUMN id SET DEFAULT nextval('public.scraping_logs_id_seq'::regclass);


--
-- Name: short_positions id; Type: DEFAULT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.short_positions ALTER COLUMN id SET DEFAULT nextval('public.short_positions_id_seq'::regclass);


--
-- Name: subscriptions id; Type: DEFAULT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.subscriptions ALTER COLUMN id SET DEFAULT nextval('public.subscriptions_id_seq'::regclass);


--
-- Name: analytics_cache analytics_cache_pkey; Type: CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.analytics_cache
    ADD CONSTRAINT analytics_cache_pkey PRIMARY KEY (id);


--
-- Name: companies companies_pkey; Type: CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_pkey PRIMARY KEY (id);


--
-- Name: countries countries_pkey; Type: CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.countries
    ADD CONSTRAINT countries_pkey PRIMARY KEY (id);


--
-- Name: managers managers_pkey; Type: CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.managers
    ADD CONSTRAINT managers_pkey PRIMARY KEY (id);


--
-- Name: scraping_logs scraping_logs_pkey; Type: CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.scraping_logs
    ADD CONSTRAINT scraping_logs_pkey PRIMARY KEY (id);


--
-- Name: short_positions short_positions_pkey; Type: CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.short_positions
    ADD CONSTRAINT short_positions_pkey PRIMARY KEY (id);


--
-- Name: subscriptions subscriptions_pkey; Type: CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.subscriptions
    ADD CONSTRAINT subscriptions_pkey PRIMARY KEY (id);


--
-- Name: idx_cache_expires; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_cache_expires ON public.analytics_cache USING btree (expires_at);


--
-- Name: idx_company_country; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_company_country ON public.companies USING btree (country_id);


--
-- Name: idx_company_isin; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_company_isin ON public.companies USING btree (isin);


--
-- Name: idx_position_active; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_position_active ON public.short_positions USING btree (is_active);


--
-- Name: idx_position_company; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_position_company ON public.short_positions USING btree (company_id);


--
-- Name: idx_position_country; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_position_country ON public.short_positions USING btree (country_id);


--
-- Name: idx_position_date; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_position_date ON public.short_positions USING btree (date);


--
-- Name: idx_position_date_active; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_position_date_active ON public.short_positions USING btree (date, is_active);


--
-- Name: idx_position_manager; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_position_manager ON public.short_positions USING btree (manager_id);


--
-- Name: idx_subscription_active; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_subscription_active ON public.subscriptions USING btree (is_active);


--
-- Name: idx_subscription_email; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX idx_subscription_email ON public.subscriptions USING btree (email);


--
-- Name: ix_analytics_cache_cache_key; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE UNIQUE INDEX ix_analytics_cache_cache_key ON public.analytics_cache USING btree (cache_key);


--
-- Name: ix_analytics_cache_id; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_analytics_cache_id ON public.analytics_cache USING btree (id);


--
-- Name: ix_companies_id; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_companies_id ON public.companies USING btree (id);


--
-- Name: ix_companies_isin; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_companies_isin ON public.companies USING btree (isin);


--
-- Name: ix_countries_code; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE UNIQUE INDEX ix_countries_code ON public.countries USING btree (code);


--
-- Name: ix_countries_id; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_countries_id ON public.countries USING btree (id);


--
-- Name: ix_managers_id; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_managers_id ON public.managers USING btree (id);


--
-- Name: ix_managers_name; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_managers_name ON public.managers USING btree (name);


--
-- Name: ix_managers_slug; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE UNIQUE INDEX ix_managers_slug ON public.managers USING btree (slug);


--
-- Name: ix_scraping_logs_id; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_scraping_logs_id ON public.scraping_logs USING btree (id);


--
-- Name: ix_short_positions_date; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_short_positions_date ON public.short_positions USING btree (date);


--
-- Name: ix_short_positions_id; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_short_positions_id ON public.short_positions USING btree (id);


--
-- Name: ix_subscriptions_email; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_subscriptions_email ON public.subscriptions USING btree (email);


--
-- Name: ix_subscriptions_id; Type: INDEX; Schema: public; Owner: jpdib
--

CREATE INDEX ix_subscriptions_id ON public.subscriptions USING btree (id);


--
-- Name: companies companies_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.companies
    ADD CONSTRAINT companies_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: scraping_logs scraping_logs_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.scraping_logs
    ADD CONSTRAINT scraping_logs_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: short_positions short_positions_company_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.short_positions
    ADD CONSTRAINT short_positions_company_id_fkey FOREIGN KEY (company_id) REFERENCES public.companies(id);


--
-- Name: short_positions short_positions_country_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.short_positions
    ADD CONSTRAINT short_positions_country_id_fkey FOREIGN KEY (country_id) REFERENCES public.countries(id);


--
-- Name: short_positions short_positions_manager_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: jpdib
--

ALTER TABLE ONLY public.short_positions
    ADD CONSTRAINT short_positions_manager_id_fkey FOREIGN KEY (manager_id) REFERENCES public.managers(id);


--
-- PostgreSQL database dump complete
--

