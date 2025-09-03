/**
 * @file This file handles all outbound API requests.
 */

/**
 * A utility for making fetch requests with retry logic.
 *
 * @param url - The URL to fetch.
 * @param options - The options for the fetch request.
 * @returns A promise that resolves with the response.
 */
async function fetchWithRetry(url: string, options?: RequestInit): Promise<Response> {
  // In a real implementation, this would have retry logic.
  console.log(`Fetching ${url} with options: ${JSON.stringify(options)}`);
  return fetch(url, options);
}

/**
 * An interface for a user service.
 */
interface IUserService {
  /**
   * Gets a user by their ID.
   *
   * @param id - The ID of the user to get.
   * @returns A promise that resolves with the user.
   */
  getUser(id: string): Promise<unknown>;
}

/**
 * A class that implements the IUserService interface.
 */
class UserService implements IUserService {
  private _endpoint = '/api/users';

  /**
   * Gets a user by their ID.
   *
   * @param id - The ID of the user to get.
   * @returns A promise that resolves with the user.
   */
  public async getUser(id: string): Promise<unknown> {
    try {
      const response = await fetchWithRetry(`${this._endpoint}/${id}`);
      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.error('Error fetching user:', error);
      throw error;
    }
  }
}

export default new UserService();
