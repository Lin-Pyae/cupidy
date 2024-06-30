PGDMP  1                    |            Cupidy    16.3    16.3     $           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            %           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            &           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            '           1262    16398    Cupidy    DATABASE     j   CREATE DATABASE "Cupidy" WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'C';
    DROP DATABASE "Cupidy";
                postgres    false            (           0    0    DATABASE "Cupidy"    COMMENT     _   COMMENT ON DATABASE "Cupidy" IS 'For Cupidy Dating Website(Project Management Final Project)';
                   postgres    false    3623            �            1259    16433    photos    TABLE     y   CREATE TABLE public.photos (
    photo_id integer NOT NULL,
    user_id integer NOT NULL,
    photo_url text NOT NULL
);
    DROP TABLE public.photos;
       public         heap    postgres    false            �            1259    16432    photos_photo_id_seq    SEQUENCE     �   CREATE SEQUENCE public.photos_photo_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 *   DROP SEQUENCE public.photos_photo_id_seq;
       public          postgres    false    220            )           0    0    photos_photo_id_seq    SEQUENCE OWNED BY     K   ALTER SEQUENCE public.photos_photo_id_seq OWNED BY public.photos.photo_id;
          public          postgres    false    219            �            1259    16408    profiles    TABLE     �   CREATE TABLE public.profiles (
    user_id integer NOT NULL,
    gender text,
    location text,
    profile_picture_url text,
    name text,
    birthday date
);
    DROP TABLE public.profiles;
       public         heap    postgres    false            �            1259    16420    user_profile_details    TABLE     �   CREATE TABLE public.user_profile_details (
    user_id integer NOT NULL,
    bio text,
    looking_for text,
    mbti_type text,
    interests text,
    school text,
    zodiac_sign text
);
 (   DROP TABLE public.user_profile_details;
       public         heap    postgres    false            �            1259    16400    users    TABLE     �   CREATE TABLE public.users (
    user_id integer NOT NULL,
    username text NOT NULL,
    email text NOT NULL,
    password_hash text NOT NULL
);
    DROP TABLE public.users;
       public         heap    postgres    false            �            1259    16399    users_user_id_seq    SEQUENCE     �   CREATE SEQUENCE public.users_user_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;
 (   DROP SEQUENCE public.users_user_id_seq;
       public          postgres    false    216            *           0    0    users_user_id_seq    SEQUENCE OWNED BY     G   ALTER SEQUENCE public.users_user_id_seq OWNED BY public.users.user_id;
          public          postgres    false    215            �           2604    16436    photos photo_id    DEFAULT     r   ALTER TABLE ONLY public.photos ALTER COLUMN photo_id SET DEFAULT nextval('public.photos_photo_id_seq'::regclass);
 >   ALTER TABLE public.photos ALTER COLUMN photo_id DROP DEFAULT;
       public          postgres    false    220    219    220            �           2604    16403    users user_id    DEFAULT     n   ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.users_user_id_seq'::regclass);
 <   ALTER TABLE public.users ALTER COLUMN user_id DROP DEFAULT;
       public          postgres    false    215    216    216            !          0    16433    photos 
   TABLE DATA           >   COPY public.photos (photo_id, user_id, photo_url) FROM stdin;
    public          postgres    false    220   
                 0    16408    profiles 
   TABLE DATA           b   COPY public.profiles (user_id, gender, location, profile_picture_url, name, birthday) FROM stdin;
    public          postgres    false    217   '                 0    16420    user_profile_details 
   TABLE DATA           t   COPY public.user_profile_details (user_id, bio, looking_for, mbti_type, interests, school, zodiac_sign) FROM stdin;
    public          postgres    false    218   �                 0    16400    users 
   TABLE DATA           H   COPY public.users (user_id, username, email, password_hash) FROM stdin;
    public          postgres    false    216   �        +           0    0    photos_photo_id_seq    SEQUENCE SET     B   SELECT pg_catalog.setval('public.photos_photo_id_seq', 1, false);
          public          postgres    false    219            ,           0    0    users_user_id_seq    SEQUENCE SET     ?   SELECT pg_catalog.setval('public.users_user_id_seq', 2, true);
          public          postgres    false    215            �           2606    16440    photos photos_pkey 
   CONSTRAINT     V   ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_pkey PRIMARY KEY (photo_id);
 <   ALTER TABLE ONLY public.photos DROP CONSTRAINT photos_pkey;
       public            postgres    false    220            �           2606    16414    profiles profiles_pkey 
   CONSTRAINT     Y   ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_pkey PRIMARY KEY (user_id);
 @   ALTER TABLE ONLY public.profiles DROP CONSTRAINT profiles_pkey;
       public            postgres    false    217            �           2606    16426 .   user_profile_details user_profile_details_pkey 
   CONSTRAINT     q   ALTER TABLE ONLY public.user_profile_details
    ADD CONSTRAINT user_profile_details_pkey PRIMARY KEY (user_id);
 X   ALTER TABLE ONLY public.user_profile_details DROP CONSTRAINT user_profile_details_pkey;
       public            postgres    false    218            �           2606    16407    users users_pkey 
   CONSTRAINT     S   ALTER TABLE ONLY public.users
    ADD CONSTRAINT users_pkey PRIMARY KEY (user_id);
 :   ALTER TABLE ONLY public.users DROP CONSTRAINT users_pkey;
       public            postgres    false    216            �           2606    16441    photos photos_user_id_fkey    FK CONSTRAINT     ~   ALTER TABLE ONLY public.photos
    ADD CONSTRAINT photos_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 D   ALTER TABLE ONLY public.photos DROP CONSTRAINT photos_user_id_fkey;
       public          postgres    false    220    216    3459            �           2606    16415    profiles profiles_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.profiles
    ADD CONSTRAINT profiles_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 H   ALTER TABLE ONLY public.profiles DROP CONSTRAINT profiles_user_id_fkey;
       public          postgres    false    216    217    3459            �           2606    16427 6   user_profile_details user_profile_details_user_id_fkey    FK CONSTRAINT     �   ALTER TABLE ONLY public.user_profile_details
    ADD CONSTRAINT user_profile_details_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);
 `   ALTER TABLE ONLY public.user_profile_details DROP CONSTRAINT user_profile_details_user_id_fkey;
       public          postgres    false    216    3459    218            !      x������ � �         �   x�m̽
�0@�9y�� M��֭TD�8	rmR�GP��8
��IrRɈO������w�Dt�1m9Ǘr�b}�/A�k\�ݔ�ęʀ]@"�N0!KtC���1$���SC�_T�2��L��l[&&z�)���5�           x�]��j�0��z�R�^atб��v�A/j�8Zm)�r���������OOn!ko3&�B�`ĜY� �Z��C���'B�1iWZ�[��z[����I�`�P3d�0�Q�-J�B�x8��3��hP��'�Ҳ����u_���v�a��q�.���gM7�ӍlQTWOzX�H~���5��x�>�p��&����~Ƞ��p�V�� �&+��nwz=�s�������P���ѽh����m����m         E   x�3����ȋO�O3R+srR���s93�3RS�����R��8��R�s3K2�L��c���� v�!�     