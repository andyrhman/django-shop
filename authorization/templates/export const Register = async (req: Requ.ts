export const Register = async (req: Request, res: Response) => {
    const body = req.body;
    const input = plainToClass(RegisterDto, body);
    const validationErrors = await validate(input);

    if (validationErrors.length > 0) {
      // Use the utility function to format and return the validation errors
      return res.status(400).json(formatValidationErrors(validationErrors));
    }

    const existingUser = await myDataSource
      .getRepository(User)
      .findOne({ where: { username: body.username, email: body.email } });

    if (existingUser) {
      return res.status(400).send("Username or email already exists");
    }

    const hashPassword = await argon2.hash(body.password);

    const user = await myDataSource.getRepository(User).save({
      fullName: body.fullName,
      username: body.username.toLowerCase(),
      email: body.email.toLowerCase(),
      password: hashPassword,
    });

    delete user.password;

    eventEmitter.emit("user.created", user);
    res.send(user);
};