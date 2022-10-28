package com.pierrot.ateco.service;

import com.pierrot.ateco.domain.UserDto;

public interface UserService {
	public void addUser(UserDto user) throws Exception;
	public UserDto getUser(String email) throws Exception;
}
